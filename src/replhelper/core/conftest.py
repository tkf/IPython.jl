import pytest

from . import get_cached_api


@pytest.fixture
def julia():
    """ pytest fixture for providing a `JuliaAPI` instance. """
    julia = get_cached_api()
    if julia is None:
        pytest.skip("JuliaAPI is not initialized.")
    return julia
# JuliaAPI has to be initialized elsewhere (e.g., in top-level conftest.py)


@pytest.fixture
def Main(julia):
    """ pytest fixture for providing a Julia `Main` name space. """
    return julia.Main
