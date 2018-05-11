import pytest

from replhelper import print_instruction_on_import_error


def test_ipython_not_found(capsys):
    @print_instruction_on_import_error
    def ipython_not_found():
        raise ImportError(name='IPython')

    ipython_not_found()

    out, err = capsys.readouterr()
    assert 'Python package IPython cannot be imported' in out
    assert 'IPython.install_dependency("ipython")' in out
    assert err == ""


def test_julia_not_found(capsys):
    @print_instruction_on_import_error
    def julia_not_found():
        raise ImportError(name='julia')

    julia_not_found()

    out, err = capsys.readouterr()
    assert 'Python package julia cannot be imported' in out
    assert 'IPython.install_dependency("julia")' in out
    assert err == ""


def test_unexpected_exception():
    class Unexpected(Exception):
        pass

    @print_instruction_on_import_error
    def exception():
        raise Unexpected()

    with pytest.raises(Unexpected):
        exception()
