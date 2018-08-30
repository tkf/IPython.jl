from .core import get_cached_api

try:
    from .key_bindings import register_key_bindings
except ImportError:
    def register_key_bindings(_):
        return lambda: None


def _unregister_key_bindings():
    """ No-op placeholder function to be replaced. """


def julia_completer(julia, self, event):
    pos = event.text_until_cursor.find("Main.eval")
    if pos < 0:
        return []
    pos += len("Main.eval('")  # pos: beginning of Julia code
    julia_code = event.line[pos:]
    julia_pos = len(event.text_until_cursor) - pos
    completions = julia.completions(julia_code, julia_pos)
    if "." in event.symbol:
        # When completing "Base.Enums.s" we need to add prefix "Base.Enums"
        prefix = event.symbol.rsplit(".", 1)[0]
        completions = [".".join((prefix, c)) for c in completions]
    else:
        completions = list(completions)
    global last_completions, last_event
    last_completions = completions
    last_event = event
    return completions
# See:
# IPython.core.completer.dispatch_custom_completer


def _julia_completer(self, event):
    return julia_completer(get_cached_api(), self, event)


def load_ipython_extension(ip):
    global _unregister_key_bindings
    _unregister_key_bindings = register_key_bindings(ip)

    ip.set_hook("complete_command", _julia_completer,
                re_key=r""".*\bMain\.eval\(["']""")
# See:
# https://ipython.readthedocs.io/en/stable/api/generated/IPython.core.hooks.html
# IPython.core.interactiveshell.init_completer
# IPython.core.completerlib (quick_completer etc.)


def unload_ipython_extension(ip):
    _unregister_key_bindings()
