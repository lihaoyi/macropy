"""This is the root directory of the project, and directly contains a bunch of
stable, useful and well-tested macros. It also sets up the import hooks that are
required for macros to run properly"""


def activate():
    import core.macros
    import core.cleanup
    import core.exact_src
    import core.gen_sym

    import core.import_hooks
    import sys
    sys.meta_path.append(core.import_hooks.MacroFinder)
    import core.hquotes
    import core.failure

def console():
    from macropy.core.console import MacroConsole
    MacroConsole().interact("0=[]=====> MacroPy Enabled <=====[]=0")


import core.exporters

__version__ = "1.0.3"
exporter = core.exporters.NullExporter()