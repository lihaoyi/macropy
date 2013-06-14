"""This is the root directory of the project, and directly contains a bunch of
stable, useful and well-tested macros. It also sets up the import hooks that are
required for macros to run properly"""
import sys
import core.import_hooks
import core.exporters
import os
sys.meta_path.append(core.import_hooks.MacroFinder)
__version__ = "0.2.0"
exporter = core.exporters.NullExporter(os.getcwd())