import pytest

from ..ipyext import julia_completer

try:
    from types import SimpleNamespace
except ImportError:
    from argparse import Namespace as SimpleNamespace

try:
    string_types = (unicode, str)
except NameError:
    string_types = (str,)


def make_event(line, text_until_cursor=None, symbol=""):
    if text_until_cursor is None:
        text_until_cursor = line
    return SimpleNamespace(
        line=line,
        text_until_cursor=text_until_cursor,
        symbol=symbol,
    )


completable_events = [
    make_event('Main.eval("'),
    make_event('Main.eval("Base.'),
]

uncompletable_events = [
    make_event(''),
    make_event('Main.eval("', text_until_cursor="Main.e"),
]


@pytest.mark.parametrize("event", completable_events)
def test_completable_events(julia, event):
    dummy_ipython = None
    completions = julia_completer(julia, dummy_ipython, event)
    assert isinstance(completions, list)
    assert completions
    assert set(map(type, completions)) == set(string_types)


@pytest.mark.parametrize("event", uncompletable_events)
def test_uncompletable_events(julia, event):
    dummy_ipython = None
    completions = julia_completer(julia, dummy_ipython, event)
    assert isinstance(completions, list)
    assert not completions
