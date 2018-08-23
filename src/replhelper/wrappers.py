from types import FunctionType
import functools


unspecified = object()


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

    def __peal(self, other):
        if isinstance(other, JuliaObject):
            return other.__jlwrap
        return other

    def __str__(self):
        return self.__julia.string(self.__jlwrap)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                self.__julia.repr(self.__jlwrap))

    @property
    def __doc__(self):
        return self.__jlwrap.__doc__

    def __getattr__(self, name):
        return self.__julia.getattr(self.__jlwrap, name)

    def __dir__(self):
        return self.__julia.py_names(self.__jlwrap)

    def __call__(self, *args, **kwargs):
        return self.__jlwrap(*args, **kwargs)

    def __len__(self):
        return len(self.__jlwrap)

    def __getitem__(self, key):
        if not isinstance(key, tuple):
            key = (key,)
        return self.__julia.getindex(self.__jlwrap, *key)

    def __setitem__(self, key, value):
        if not isinstance(key, tuple):
            key = (key,)
        self.__julia.setindex_b(self.__jlwrap, value, *key)

    def __delitem__(self, key):
        if not isinstance(key, tuple):
            key = (key,)
        self.__julia.delete_b(self.__jlwrap, *key)

    def __contains__(self, item):
        return self.__julia.eval("in")(self.__jlwrap, item)

    def __add__(self, other):
        return self.__julia.eval("+")(self.__jlwrap, other)

    def __sub__(self, other):
        return self.__julia.eval("-")(self.__jlwrap, other)

    def __mul__(self, other):
        return self.__julia.eval("*")(self.__jlwrap, other)

    # def __matmul__(self, other):
    #     return self.__julia.eval("???")(self.__jlwrap, other)

    def __truediv__(self, other):
        return self.__julia.eval("/")(self.__jlwrap, other)

    def __floordiv__(self, other):
        return self.__julia.eval("//")(self.__jlwrap, other)

    def __mod__(self, other):
        return self.__julia.eval("mod")(self.__jlwrap, other)

    def __divmod__(self, other):
        return self.__julia.eval("divrem")(self.__jlwrap, other)

    def __pow__(self, other, modulo=unspecified):
        if modulo is unspecified:
            return self.__julia.eval("^")(self.__jlwrap, other)
        else:
            return self.__julia.eval("powermod")(self.__jlwrap, other, modulo)

    def __lshift__(self, other):
        return self.__julia.eval("<<")(self.__jlwrap, other)

    def __rshift__(self, other):
        return self.__julia.eval(">>")(self.__jlwrap, other)

    def __and__(self, other):
        return self.__julia.eval("&")(self.__jlwrap, other)

    def __xor__(self, other):
        return self.__julia.eval("xor")(self.__jlwrap, other)

    def __or__(self, other):
        return self.__julia.eval("|")(self.__jlwrap, other)


def make_wrapper(fun):
    @functools.wraps(fun)
    def wrapper(self, *args, **kwds):
        # Peal off all arguments if they are wrapped by JuliaObject.
        # This is required for, e.g., Main.map(Main.identity, range(3))
        # to work.
        peal = self._JuliaObject__peal
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
    setattr(JuliaObject, name, make_wrapper(fun))
