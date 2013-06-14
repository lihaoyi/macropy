"""Plumbing related to hooking into the import process, unrelated to MacroPy"""

import sys
import imp
import ast
import macropy
from macros import *
from util import *


class _MacroLoader(object):
    """Performs the loading of a module with macro expansion."""
    def __init__(self, package_path, tree, source, file_name, bindings):
        self.package_path = package_path
        self.tree = tree
        self.source = source
        self.file_name = file_name
        self.bindings = bindings


    def load_module(self, fullname):

        for (p, _) in self.bindings:
            __import__(p)

        modules = [(sys.modules[p], bindings) for (p, bindings) in self.bindings]


        tree = expand_entire_ast(self.tree, self.source, modules)

        ispkg = False
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = []
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        mod.__file__ = self.file_name
        macropy.exporter.export_transformed(tree, fullname, self.file_name)
        try:
            exec compile(tree, self.file_name, "exec") in mod.__dict__
        except Exception as e:
            import traceback
            traceback.print_exc()

        return mod


@singleton
class MacroFinder(object):
    """Loads a module and looks for macros inside, only providing a loader if
    it finds some."""
    def find_module(self, module_name, package_path):
        try:
            (file, pathname, description) = imp.find_module(
                module_name.split('.')[-1],
                package_path
            )
            txt = file.read()

            # short circuit heuristic to fail fast if the source code can't
            # possible contain the macro import at all
            if "macros" not in txt:
                return

            # check properly the AST if the macro import really exists
            tree = ast.parse(txt)

            bindings = detect_macros(tree)

            if bindings == []:
                return # no macros found, carry on
            else:
                return _MacroLoader(module_name, tree, txt, file.name, bindings)
        except Exception, e:
            pass
