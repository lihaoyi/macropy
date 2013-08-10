"""This is the root directory of the project, and directly contains a bunch of
stable, useful and well-tested macros. It also sets up the import hooks that are
required for macros to run properly"""


def activate():
    from .core import macros
    from .core import cleanup
    from .core import exact_src
    from .core import gen_sym

    from .core import import_hooks
    import sys
    sys.meta_path.insert(0, import_hooks.MacroFinder)
    import macropy
    from .core import hquotes
    from .core import failure

def console():
    from macropy.core.console import MacroConsole
    MacroConsole().interact("0=[]=====> MacroPy Enabled <=====[]=0")


from .core import exporters

__version__ = "1.0.3"
exporter = exporters.NullExporter()