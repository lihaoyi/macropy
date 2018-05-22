# -*- coding: utf-8 -*-
"""This is the root directory of the project, and directly contains a
bunch of stable, useful and well-tested macros. It also sets up the
import hooks that are required for macros to run properly.
"""


def activate():
    from .core import macros  # noqa
    from .core import cleanup  # noqa
    from .core import exact_src  # noqa
    from .core import gen_sym  # noqa

    from .core import import_hooks
    import sys
    sys.meta_path.insert(0, import_hooks.MacroFinder)
    import macropy  # noqa
    from .core import hquotes  # noqa
    from .core import failure  # noqa


def console():
    from macropy.core.console import MacroConsole
    MacroConsole().interact("0=[]=====> MacroPy Enabled <=====[]=0")


from .core import exporters  # noqa

__version__ = "1.1.0b2"
exporter = exporters.NullExporter()
