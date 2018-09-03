import os

from .utils import Singleton, reloadall
from .julia_api import JuliaAPI, JuliaMain


class APIInitializer(Singleton):

    def __init__(self, *args, **kwargs):
        self.api = JuliaAPI(*args, **kwargs)

    @classmethod
    def with_pyjulia(cls, *args, **kwargs):
        """
        Initialize `.JuliaAPI` using PyJulia.
        """
        from julia.core import Julia
        julia = Julia(*args, **kwargs)

        julia_api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "julia_api.jl")
        api, eval_str = julia.eval("""
        path -> let m = Module()
            Base.include(m, path)
            (m.JuliaAPI, m.JuliaAPI.eval_str)
        end
        """)(julia_api_path)
        return cls.instance(eval_str, api)


def get_api(*args, **kwargs):
    """
    Initialize `.JuliaAPI`.

    Positional and keyword arguments are passed directly to `julia.Julia`

    >>> from ipyjulia_hacks import get_api
    >>> get_api(jl_runtime_path="PATH/TO/CUSTOM/JULIA") # doctest: +SKIP
    <JuliaAPI ...>
    """
    return get_cached_api() or \
        APIInitializer.with_pyjulia(*args, **kwargs).api


def get_cached_api():
    """
    Get pre-initialized `.JuliaAPI` instance or `None` if not ready.

    .. (this is for checking availability in doctest)
       >>> _ = getfixture("julia")

    >>> from ipyjulia_hacks import get_cached_api
    >>> jlapi = get_cached_api()
    >>> jlapi.eval("1 + 1")
    2
    """
    initializer = APIInitializer.initialized()
    if initializer is not None:
        return initializer.api


class JuliaMainInitializer(Singleton):

    def __init__(self, *args, **kwargs):
        self.Main = JuliaMain(get_api(*args, **kwargs))


def get_main(*args, **kwargs):
    return JuliaMainInitializer.instance(*args, **kwargs).Main


def get_cached_main():
    if get_cached_api() is not None:
        return get_main()


def revise():
    """Ad-hoc hot reload."""
    from .. import core  # assuming this subpackage is called "core"
    reloadall(core, [
        core.utils,
        core.wrappers,
        core.julia_api,
        core.initializer,
    ])
