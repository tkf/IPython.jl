from __future__ import print_function

import sys


def jl_name(name):
    if name.endswith('_b'):
        return name[:-2] + '!'
    return name


class JuliaNameSpace(object):

    def __init__(self, julia):
        self.__julia = julia

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super(JuliaNameSpace, self).__setattr__(name, value)
        else:
            setter = '''
            Main.PyCall.pyfunctionret(
                (x) -> eval(:({} = $x)),
                Any,
                PyCall.PyAny)
            '''.format(jl_name(name))
            self.__julia.eval(setter)(value)

    def __getattr__(self, name):
        if name.startswith('_'):
            return super(JuliaNameSpace, self).__getattr__(name)
        else:
            return self.__julia.eval(jl_name(name))


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


def ipython_options(**kwargs):
    from traitlets.config import Config
    from julia import Julia

    julia = Julia(**kwargs)
    Main = JuliaNameSpace(julia)
    user_ns = dict(
        julia=julia,
        Main=Main,
    )

    c = Config()
    c.TerminalIPythonApp.display_banner = False
    c.TerminalInteractiveShell.confirm_exit = False

    return dict(user_ns=user_ns, config=c)


@print_instruction_on_import_error
def customized_ipython(**kwargs):
    import IPython
    print()
    IPython.start_ipython(**ipython_options(**kwargs))


@print_instruction_on_import_error
def customized_ptipython(**kwargs):
    from ptpython.ipython import embed
    print()
    embed(**ipython_options(**kwargs))
# https://github.com/jonathanslenders/ptpython/blob/master/ptpython/entry_points/run_ptipython.py
# https://github.com/jonathanslenders/ptpython/blob/master/ptpython/ipython.py
