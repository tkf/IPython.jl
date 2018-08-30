import pytest

from ..core import get_main


@pytest.fixture
def Main():
    """ pytest fixture for providing a Julia `Main` name space. """
    Main = get_main()
    if Main is None:
        pytest.skip("Main not configured (not called from IPython.jl?)")
    else:
        return Main
