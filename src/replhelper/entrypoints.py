from .convenience import with_message
from .core import get_main


def ipython_options(**kwargs):
    from traitlets.config import Config

    user_ns = dict(
        Main=get_main(**kwargs),
    )

    c = Config()
    c.TerminalIPythonApp.display_banner = False
    c.TerminalIPythonApp.matplotlib = None  # don't close figures
    c.TerminalInteractiveShell.confirm_exit = False

    from . import ipyext
    c.InteractiveShellApp.extensions = [
        ipyext.__name__,
    ]

    return dict(user_ns=user_ns, config=c)


@with_message
def customized_ipython(**kwargs):
    import IPython
    print()
    IPython.start_ipython(**ipython_options(**kwargs))
