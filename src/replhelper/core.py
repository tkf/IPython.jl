# TODO: replace object.__XXX__(self, ...) with super().__XXX__(...)
# once Python 2 support is removed.

from __future__ import print_function

import sys
import types

try:
    from importlib import reload
except ImportError:
    try:
        from imp import reload
    except ImportError:
        pass  # Python 2?

from .wrappers import JuliaObject

_Main = None


def jl_name(name):
    if name.endswith('_b'):
        return name[:-2] + '!'
    return name


def py_name(name):
    if name.endswith('!'):
        return name[:-1] + '_b'
    return name


class JuliaAPI(object):

    def __init__(self, eval_str, api):
        self.eval = eval_str
        self.api = api
        # After this point, self.<julia_name> works:
        self.jlwrap_type = type(self.get_jlwrap_prototype())
        self.getproperty = self.getproperty_str

    def __getattr__(self, name):
        try:
            # return super().__getattr__(name, value)
            return object.__getattr__(self, name)
        except AttributeError:
            return self.eval(self.api, jl_name(name))

    def py_names(self, obj):
        names = self.dir(obj)
        names = map(py_name, names)
        if sys.version_info.major == 3:
            names = filter(str.isidentifier, names)
        return names

    def isjlwrap(self, obj):
        return isinstance(obj, self.jlwrap_type)

    def maybe_wrap(self, obj):
        if self.isjlwrap(obj):
            return JuliaObject(obj, self)
        else:
            return obj

    def getattr(self, obj, name):
        return self.maybe_wrap(self.getproperty(obj, jl_name(name)))


class JuliaNameSpace(object):

    """
    Interface to Julia name space.

    Examples::

        Main.xs = [1, 2, 3]
        Main.map(lambda x: x ** 2, [1, 2, 3])
        Main.eval("Vector{Int}")([1.0, 2.0, 3.0])
        Main.eval("x -> x.^2")([1, 2, 3])

    """

    def __init__(self, julia):
        self.__julia = julia  # JuliaAPI

    def eval(self, code, wrap=True, **kwargs):
        """
        Evaluate `code` in `Main` scope of Julia.

        Parameters
        ----------
        code : str
            Julia code to be evaluated.

        Keyword Arguments
        -----------------
        wrap : bool
            If `True` (default), wrap the output by a Python interface
            (`JuliaObject`) for some appropriate Julia objects.

        """
        ans = self.__julia.eval(code, **kwargs)
        if wrap:
            return self.__julia.maybe_wrap(ans)
        return ans

    # def __getitem__(self, code):
    #     return self.eval(code)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            # super().__setattr__(name, value)
        else:
            self.__julia.set_var(name, value)

    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattr__(self, name)
            # return super().__getattr__(name)
        else:
            Main = self.__julia.eval('Main')
            return self.__julia.getattr(Main, name)

    @property
    def __all__(self):
        Main = self.__julia.eval("Main")
        return list(self.__julia.py_names(Main))

    def __dir__(self):
        if sys.version_info.major == 2:
            names = set()
        else:
            names = set(super().__dir__())
        names.update(self.__all__)
        return list(names)
    # Override __dir__ method so that completing member names work
    # well in Python REPLs like IPython.


def get_api(main):
    if main is None:
        return None
    return main._JuliaNameSpace__julia


def get_cached_api():
    return get_api(_Main)


def get_main(**kwargs):
    """
    Create or get cached `Main`.

    Caching is required to avoid re-writing to `_Main` when re-entering
    to IPython session (where `user_ns` would be ignored).
    """
    global _Main
    if _Main is None:
        _Main = JuliaNameSpace(JuliaAPI(**kwargs))
    return _Main


def revise():
    """Ad-hoc hot reload."""
    import replhelper
    Main = _Main
    reload(replhelper.wrappers)
    reload(replhelper.core)
    reload(replhelper.ipyext)
    reload(replhelper)

    if Main is not None:
        Main.__class__ = replhelper.core.JuliaNameSpace
        Main._JuliaNameSpace__julia.__class__ = replhelper.core.JuliaAPI
        replhelper.core._Main = Main

    try:
        replhelper.tests
    except AttributeError:
        return

    # *Try* reloading modules `replhelper.tests.*`.  If there are
    # dependencies between those modules, it's not going to work.
    for (name, module) in sorted(vars(replhelper.tests).items(),
                                 key=lambda pair: pair[0]):
        if isinstance(module, types.ModuleType):
            reload(module)
