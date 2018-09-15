import pytest

from .. import core
from .. import ipyext


@pytest.fixture
def Main():
    """ pytest fixture for providing a Julia `Main` name space. """
    if core._Main is None:
        pytest.skip("Main not configured (not called from IPython.jl?)")
    else:
        return core._Main


@pytest.fixture
def julia(Main):
    """ pytest fixture for providing a `JuliaAPI` instance. """
    return core.get_api(Main)


@pytest.fixture(scope="session")
def ipy_with_magic():
    Main()  # check if Julia API is ready
    from IPython.testing.globalipapp import get_ipython
    ip = get_ipython()
    ipyext.load_ipython_extension(ip)
    return ip
