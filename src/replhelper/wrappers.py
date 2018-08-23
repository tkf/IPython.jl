from types import FunctionType
import functools


unspecified = object()


class JuliaObject(object):

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
        return "<{} {}>".format(self.__class__.__name__, self)

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
        return self.__jlwrap[key]

    def __setitem__(self, key, value):
        self.__jlwrap[key] = value

    def __delitem__(self, key):
        del self.__jlwrap[key]

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
        peal = self._JuliaObject__peal
        args = [peal(a) for a in args]
        kwds = {k: peal(v) for (k, v) in kwds.items()}
        return fun(self, *args, **kwds)
    return wrapper


for name, fun in vars(JuliaObject).items():
    if name in ('__module__', '__init__'):
        continue
    if name.startswith('_JuliaObject__'):
        continue
    if not isinstance(fun, FunctionType):
        continue
    setattr(JuliaObject, name, make_wrapper(fun))
