import pytest

from .. import core


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
