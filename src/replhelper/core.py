# TODO: replace object.__XXX__(self, ...) with super().__XXX__(...)
# once Python 2 support is removed.

from __future__ import print_function

import sys
import types
import warnings

try:
    from importlib import reload
except ImportError:
    try:
        from imp import reload
    except ImportError:
        pass  # Python 2?

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

    def __init__(self, eval_str, set_var):
        self.eval = eval_str
        self.set_var = set_var


class JuliaNameSpace(object):

    def __init__(self, julia):
        self.__julia = julia

    eval = property(lambda self: self.__julia.eval)

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
            return self.__julia.eval(jl_name(name))

    @property
    def __all__(self):
        names = self.__julia.eval("names(Main)")
        return list(map(py_name, names))

    def __dir__(self):
        if sys.version_info.major == 2:
            names = set()
        else:
            names = set(super().__dir__())
        names.update(self.__all__)
        return list(names)
    # Override __dir__ method so that completing member names work
    # well in Python REPLs like IPython.


instruction_template = """

Python package "{package}" cannot be imported from Python interpreter
{python}.
{additional_message}
Use your favorite method to install "{need_install}" or run the following
command in Julia (which *tries* to the right thing):

    IPython.install_dependency("{need_install}")

It prints the installation command to be executed and prompts your
input (yes/no) before really executing it.
"""

ipython_dependency_missing = """
IPython (version: {IPython.__version__}) is importable but {dependency}
cannot be imported.  It is very strange and I'm not sure what is the
best instruction here.  Updating IPython could help.
"""


def make_instruction(package, need_install=None, **kwargs):
    return instruction_template.format(**dict(dict(
        package=package,
        need_install=need_install or package.lower(),
        python=sys.executable,
        additional_message='',
    ), **kwargs))


def make_dependency_missing_instruction(IPython, dependency):
    return make_instruction(
        dependency,
        need_install='ipython',
        additional_message=ipython_dependency_missing.format(
            IPython=IPython,
            dependency=dependency,
        ))


def package_name(err):
    try:
        return err.name
    except AttributeError:
        # Python 2 support:
        prefix = 'No module named '
        message = str(err)
        if message.startswith(prefix):
            return message[len(prefix):].rstrip()
    raise ValueError('Cannot determine missing package for error {}'
                     .format(err))


def print_instruction_on_import_error(f):
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ImportError as err:
            name = package_name(err)
            if name in ('IPython', 'julia'):
                print(make_instruction(name))
                return
            if name == 'traitlets':
                try:
                    import IPython
                except ImportError:
                    print(make_instruction('IPython'))
                    return
                print(make_dependency_missing_instruction(IPython, name))
                return
            raise
    return wrapped


def get_api(main):
    if main is None:
        return None
    return main._JuliaNameSpace__julia


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


def ipython_options(**kwargs):
    global _Main
    from traitlets.config import Config

    _Main = Main = JuliaNameSpace(JuliaAPI(**kwargs))
    user_ns = dict(
        Main=Main,
    )

    c = Config()
    c.TerminalIPythonApp.display_banner = False
    c.TerminalInteractiveShell.confirm_exit = False

    return dict(user_ns=user_ns, config=c)


segfault_warning = """\
Segmentation fault warning.

You are using IPython version {IPython.__version__} which is known to
cause segmentation fault with tab completion.  For segfault-free
IPython, upgrade to version 7 or above (which may still be in
development stage depending on the time you read this message).
Note also that IPython releases after 5.x do not support Python 2.

If you need to install development version of IPython and understand
what would happen to your Python environment by doing so, executing
the following command in Julia may help:

    IPython.install_dependency("ipython-dev")

It prints the installation command to be executed and prompts your
input (yes/no) before really executing it.
"""

segfault_warned = False


@print_instruction_on_import_error
def customized_ipython(**kwargs):
    global segfault_warned
    import IPython
    print()
    if int(IPython.__version__.split('.', 1)[0]) < 7 and not segfault_warned:
        warnings.warn(segfault_warning.format(**vars()))
        segfault_warned = True
    IPython.start_ipython(**ipython_options(**kwargs))


def revise():
    """Ad-hoc hot reload."""

    Main = _Main

    import replhelper
    reload(replhelper.core)

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

    reload(replhelper)
