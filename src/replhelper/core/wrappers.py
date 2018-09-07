# -*- coding: utf-8 -*-

"""
Pythonic wrapper of Julia objects.

.. (this is for checking availability in doctest)
   >>> _ = getfixture("julia")

>>> from ipyjulia_hacks import get_api
>>> jlapi = get_api()

**Mutables**:

>>> spam = jlapi.eval('''eval(Module(), quote
... mutable struct Spam
...     egg
... end
... Spam(1)
... end)''')
>>> spam.egg
1
>>> spam.egg = 2
>>> spam.egg
2

**Numbers**:

>>> one = jlapi.eval("1", wrap=True)
>>> one
<JuliaObject 1>
>>> one // 2  # translated to ``1 ÷ 2``, *not* ``1 // 2``
0
>>> assert one == 1
>>> assert one != 0
>>> assert one > 0
>>> assert one >= 1
>>> assert one < 2
>>> assert one <= 1
>>> assert one

**Arrays**:

>>> a2d = jlapi.eval("reshape((1:6) .- 1, (2, 3))")
>>> a2d
<JuliaObject [0 2 4; 1 3 5]>
>>> a2d[0, 1]
2
>>> jlapi.eval("[1, 2, 3]")
array([1, 2, 3], dtype=int64)
>>> arr = jlapi.eval("[1, 2, 3]", wrap=True)
>>> list(reversed(arr))
[3, 2, 1]

**Linear algebra**:

>>> jlapi.eval("import LinearAlgebra")
>>> I = jlapi.eval("LinearAlgebra.I")
>>> M = jlapi.eval("reshape(1:6, 2, 3)")
>>> Y = M @ I
>>> Y
array([[1, 3, 5],
       [2, 4, 6]], dtype=int64)
>>> import numpy
>>> M @ numpy.ones(3)
array([ 9., 12.])

**Named tuple**:

>>> nt = jlapi.eval("(a = 1, b = 2)")
>>> nt.a
1
>>> nt.b
2
>>> nt[0]
1
>>> nt[1]
2
>>> len(nt)
2
>>> {"a", "b"} <= set(dir(nt))
True

**Dictionary**:

>>> dct = jlapi.eval('Dict("b" => 2)')
>>> dct["a"] = 1
>>> del dct["b"]
>>> dct["a"]
1
>>> dct
<JuliaObject Dict("a"=>1)>
>>> dct == {"a": 1}
True

**Three-valued logic**:

>>> true = jlapi.eval("true", wrap=True)
>>> false = jlapi.eval("false", wrap=True)
>>> missing = jlapi.eval("missing")
>>> true
<JuliaObject true>
>>> false
<JuliaObject false>
>>> true & missing
<JuliaObject missing>
>>> false & missing
False
>>> true | missing
True
>>> false | missing
<JuliaObject missing>
>>> true ^ false
True
>>> true ^ true
False
>>> true ^ missing
<JuliaObject missing>
>>> false ^ false
False
"""

from types import FunctionType
import functools
import json


unspecified = object()


def broadcast(julia, fcode, *args):
    """ Do ``($fcode).(args...)``. """
    broadcast = julia.eval("broadcast", wrap=False)
    f = julia.eval(fcode, wrap=False)
    return julia.wrapcall(broadcast, f, *map(peal, args))


def broadcast_iop(julia, fcode, a, b):
    """ Do ``a .= ($fcode).(a, b)``. """
    broadcast_b = julia.eval("broadcast!", wrap=False)
    f = julia.eval(fcode, wrap=False)
    a = peal(a)
    b = peal(b)
    broadcast_b(f, a, a, b)


class JuliaObject(object):
    """
    Python interface for Julia object.

    Parameters
    ----------
    jlwrap : PyCall.jlwrap
        Julia object wrapped as PyCall.jlwrap.
    julia : JuliaAPI
        Python interface for calling Julia functions.

        See:
        ./core.py
        ../julia_api.jl
    """

    def __init__(self, jlwrap, julia):
        self.__jlwrap = jlwrap
        self.__julia = julia

    def __str__(self):
        return self.__julia.string(self.__jlwrap)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                self.__julia.repr(self.__jlwrap))

    # TODO: def __bytes__(self):

    @property
    def __doc__(self):
        return self.__jlwrap.__doc__

    def __getattr__(self, name):
        return self.__julia.getattr(self.__jlwrap, name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super(JuliaObject, self).__setattr__(name, value)
            return
        symbol = self.__julia.Symbol(name)
        self.__julia.setproperty_b(self.__jlwrap, symbol, value)

    # TODO: def __delattr__(self, name, value):

    def __dir__(self):
        return self.__julia.py_names(self.__jlwrap)

    def __call__(self, *args, **kwargs):
        return self.__julia.wrapcall(self.__jlwrap, *args, **kwargs)

    def __eq__(self, other):
        return self.__julia.pybroadcast("==", self.__jlwrap, other)

    def __lt__(self, other):
        return self.__julia.pybroadcast("<", self.__jlwrap, other)

    def __le__(self, other):
        return self.__julia.pybroadcast("<=", self.__jlwrap, other)

    def __ne__(self, other):
        return self.__julia.pybroadcast("!=", self.__jlwrap, other)

    def __gt__(self, other):
        return self.__julia.pybroadcast(">", self.__jlwrap, other)

    def __ge__(self, other):
        return self.__julia.pybroadcast(">=", self.__jlwrap, other)

    # TODO: def __hash__(self):

    def __bool__(self):
        return self.__julia.eval("Bool")(self.__jlwrap)

    def __len__(self):
        return self.__julia.length(self.__jlwrap)

    def __wrapkey(self, key):
        if isinstance(key, slice):
            return self.__julia.PySlice(key.start, key.stop, key.step)
        elif key is Ellipsis:
            return self.__julia.PyEllipsis()
        return key

    def __getitem__(self, key):
        if not isinstance(key, tuple):
            key = (key,)
        key = map(self.__wrapkey, key)
        return self.__julia.pygetindex(self.__jlwrap, *key)

    def __setitem__(self, key, value):
        if not isinstance(key, tuple):
            key = (key,)
        key = map(self.__wrapkey, key)
        self.__julia.pysetindex_b(self.__jlwrap, value, *key)

    def __delitem__(self, key):
        if not isinstance(key, tuple):
            key = (key,)
        self.__julia.delete_b(self.__jlwrap, *key)

    def __iter__(self):
        iterate = self.__julia.eval("iterate")
        pair = iterate(self.__jlwrap)
        while True:
            if pair is None:
                return
            yield pair[0]
            pair = iterate(self.__jlwrap, pair[1])

    def __reversed__(self):
        return self.__julia.eval("reverse")(self.__jlwrap)

    def __contains__(self, item):
        return self.__julia.eval("in")(item, self.__jlwrap)

    def __add__(self, other):
        return broadcast(self.__julia, "+", self.__jlwrap, other)

    def __sub__(self, other):
        return broadcast(self.__julia, "-", self.__jlwrap, other)

    def __mul__(self, other):
        return broadcast(self.__julia, "*", self.__jlwrap, other)

    def __matmul__(self, other):
        return self.__julia.eval("*")(self.__jlwrap, other)

    def __truediv__(self, other):
        return broadcast(self.__julia, "/", self.__jlwrap, other)

    def __floordiv__(self, other):
        """ Call `div` (`÷`), *not* `//`, in Julia. """
        return broadcast(self.__julia, "div", self.__jlwrap, other)

    def __mod__(self, other):
        return broadcast(self.__julia, "mod", self.__jlwrap, other)

    def __divmod__(self, other):
        return broadcast(self.__julia, "divrem", self.__jlwrap, other)

    def __pow__(self, other, modulo=unspecified):
        if modulo is unspecified:
            return broadcast(self.__julia, "^", self.__jlwrap, other)
        else:
            return broadcast(self.__julia, "powermod", self.__jlwrap,
                             other, modulo)

    def __lshift__(self, other):
        return broadcast(self.__julia, "<<", self.__jlwrap, other)

    def __rshift__(self, other):
        return broadcast(self.__julia, ">>", self.__jlwrap, other)

    def __and__(self, other):
        return broadcast(self.__julia, "&", self.__jlwrap, other)

    def __xor__(self, other):
        return broadcast(self.__julia, "xor", self.__jlwrap, other)

    def __or__(self, other):
        return broadcast(self.__julia, "|", self.__jlwrap, other)

    def __radd__(self, other):
        return self.__julia.eval("+")(other, self.__jlwrap)

    def __rsub__(self, other):
        return self.__julia.eval("-")(other, self.__jlwrap)

    def __rmul__(self, other):
        return self.__julia.eval("*")(other, self.__jlwrap)

    def __rmatmul__(self, other):
        return self.__julia.eval("*")(other, self.__jlwrap)

    def __rtruediv__(self, other):
        return self.__julia.eval("/")(other, self.__jlwrap)

    def __rfloordiv__(self, other):
        return self.__julia.eval("div")(other, self.__jlwrap)

    def __rmod__(self, other):
        return self.__julia.eval("mod")(other, self.__jlwrap)

    def __rdivmod__(self, other):
        return self.__julia.eval("divrem")(other, self.__jlwrap)

    def __rpow__(self, other):
        return self.__julia.eval("^")(other, self.__jlwrap)

    def __rlshift__(self, other):
        return self.__julia.eval("<<")(other, self.__jlwrap)

    def __rrshift__(self, other):
        return self.__julia.eval(">>")(other, self.__jlwrap)

    def __rand__(self, other):
        return self.__julia.eval("&")(other, self.__jlwrap)

    def __rxor__(self, other):
        return self.__julia.eval("xor")(other, self.__jlwrap)

    def __ror__(self, other):
        return self.__julia.eval("|")(other, self.__jlwrap)

    def __iadd__(self, other):
        broadcast_iop(self.__julia, "+", self, other)
        return self

    def __isub__(self, other):
        broadcast_iop(self.__julia, "-", self, other)
        return self

    def __imul__(self, other):
        broadcast_iop(self.__julia, "*", self, other)
        return self

    def __imatmul__(self, other):
        self.__julia.rmul_b(self.__jlwrap, other)
        return self

    def __itruediv__(self, other):
        broadcast_iop(self.__julia, "/", self, other)
        return self

    def __ifloordiv__(self, other):
        broadcast_iop(self.__julia, "div", self, other)
        return self

    def __imod__(self, other):
        broadcast_iop(self.__julia, "mod", self, other)
        return self

    def __ipow__(self, other, modulo=unspecified):
        if modulo is unspecified:
            broadcast_iop(self.__julia, "^", self, other)
        else:
            broadcast_iop(self.__julia, "powermod", self, other, modulo)
        return self

    def __ilshift__(self, other):
        broadcast_iop(self.__julia, "<<", self, other)
        return self

    def __irshift__(self, other):
        broadcast_iop(self.__julia, ">>", self, other)
        return self

    def __iand__(self, other):
        broadcast_iop(self.__julia, "&", self, other)
        return self

    def __ixor__(self, other):
        broadcast_iop(self.__julia, "xor", self, other)
        return self

    def __ior__(self, other):
        broadcast_iop(self.__julia, "|", self, other)
        return self

    def __neg__(self):
        return self.__julia.eval("-")(self.__jlwrap)

    def __pos__(self):
        return self.__julia.eval("+")(self.__jlwrap)

    def __abs__(self):
        return self.__julia.eval("abs")(self.__jlwrap)

    def __invert__(self):
        return self.__julia.eval("~")(self.__jlwrap)

    def __complex__(self):
        jlcomplex = self.__julia.eval("ComplexF64", wrap=False)
        return complex(peal(jlcomplex(self.__jlwrap)))

    def __int__(self):
        jlint = self.__julia.eval("Int128", wrap=False)
        return int(peal(jlint(self.__jlwrap)))

    def __float__(self):
        jlfloat = self.__julia.eval("Float64", wrap=False)
        return float(peal(jlfloat(self.__jlwrap)))

    # TODO: Use BigFloat/BigInt if mpmath is installed.

    # TODO: def __index__(self)

    def __round__(self, ndigits=None):
        if ndigits is None:
            ndigits = 0
        return self.__julia.eval("round")(self.__jlwrap, digits=ndigits)

    def __trunc__(self):
        return self.__julia.eval("trunc")(self.__jlwrap)

    def __floor__(self):
        return self.__julia.eval("floor")(self.__jlwrap)

    def __ceil__(self):
        return self.__julia.eval("ceil")(self.__jlwrap)

    def _repr_mimebundle_(self, include=None, exclude=None):
        mimes = include or [
            "text/plain",
            "text/html",
            "text/markdown",
            "text/latex",
            "application/json",
            "application/javascript",
            "application/pdf",
            "image/png",
            "image/jpeg",
            "image/svg+xml",
        ]
        exclude = exclude or []

        showable = self.__julia.eval("showable")
        showraw = self.__julia.eval("""
        (obj, mimetype) -> begin
            io = IOBuffer()
            show(IOContext(io, :color => true), mimetype, obj)
            take!(io)
        end
        """)

        format_dict = {}
        for mimetype in mimes:
            if mimetype in exclude:
                continue
            if showable(mimetype, self.__jlwrap):
                data = showraw(self.__jlwrap, mimetype)
                if (mimetype.startswith("text/") or
                        mimetype in ("application/javascript",
                                     "image/svg+xml")):
                    data = data.decode('utf8')
                elif mimetype == "application/json":
                    data = json.loads(data)
                else:
                    data = bytes(data)
                format_dict[mimetype] = data
        return format_dict

# https://ipython.readthedocs.io/en/stable/api/generated/IPython.core.formatters.html#IPython.core.formatters.DisplayFormatter.format
# https://ipython.readthedocs.io/en/stable/config/integrating.html#MyObject._repr_mimebundle_


def peal(obj):
    if isinstance(obj, JuliaObject):
        return obj._JuliaObject__jlwrap
    elif isinstance(obj, JuliaCallback):
        return peal(obj.wrap())
    else:
        return obj


def autopeal(fun):
    @functools.wraps(fun)
    def wrapper(self, *args, **kwds):
        # Peal off all arguments if they are wrapped by JuliaObject.
        # This is required for, e.g., Main.map(Main.identity, range(3))
        # to work.
        args = [peal(a) for a in args]
        kwds = {k: peal(v) for (k, v) in kwds.items()}
        return fun(self, *args, **kwds)
    return wrapper


for name, fun in vars(JuliaObject).items():
    if name in ("__module__", "__init__", "__doc__"):
        continue
    if name.startswith('_JuliaObject__'):
        continue
    if not isinstance(fun, FunctionType):
        continue
    # TODO: skip single-argument (i.e., `self`-only) methods (optimization)
    setattr(JuliaObject, name, autopeal(fun))


class JuliaCallback(object):

    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def wrap(self, force=True):
        from . import get_cached_api
        julia = get_cached_api()

        def function(*args, **kwargs):
            wargs = [julia.maybe_wrap(a) for a in args]
            wkwargs = {k: julia.maybe_wrap(v) for (k, v) in kwargs.items()}
            return peal(self.function(*wargs, **wkwargs))

        return julia.WrappingCallback(function, force)


jlfunction = JuliaCallback
