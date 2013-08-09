"""Plumbing related to hooking into the import process, unrelated to MacroPy"""

import sys
import imp
import ast
import macropy.activate
from .macros import *
import traceback

class _MacroLoader(object):
    """Performs the loading of a module with macro expansion."""
    def __init__(self, mod):
        self.mod = mod


    def load_module(self, fullname):
        self.mod.__loader__ = self
        return self.mod


@singleton
class MacroFinder(object):
    """Loads a module and looks for macros inside, only providing a loader if
    it finds some."""
    def find_module(self, module_name, package_path):
        #print("????????????????"*33)
        try:
            try:
                (file, pathname, description) = imp.find_module(
                    module_name.split('.')[-1],
                    package_path
                )

                txt = file.read()
                file.close()
            except:
                return
            # short circuit heuristic to fail fast if the source code can't
            # possible contain the macro import at all
            if "macros" not in txt:
                print("failed to find",module_name, package_path)
                return

            # check properly the AST if the macro import really exists
            tree = ast.parse(txt)

            bindings = detect_macros(tree)

            if bindings == []:
                
                return # no macros found, carry on
            #print("\n\nSEARCHING FOR ", module_name, package_path)

            mod = macropy.exporter.find(file, pathname, description, module_name, package_path)

            if mod:
                return _MacroLoader(mod)

            for (p, _) in bindings:
                __import__(p)

            modules = [(sys.modules[p], bindings) for (p, bindings) in bindings]

            tree = expand_entire_ast(tree, txt, modules)

            ispkg = False
            mod = sys.modules.setdefault(module_name, imp.new_module(module_name))

            if ispkg:
                mod.__path__ = []
                mod.__package__ = module_name
            else:
                mod.__package__ = module_name.rpartition('.')[0]
            mod.__file__ = file.name
            #from . import unparse
            print("finding",module_name, package_path)

            code = compile(tree, file.name, "exec")


            try:
                exec(code, mod.__dict__)
                macropy.exporter.export_transformed(code, tree, module_name, file.name)
            except Exception as e:

                traceback.print_exc()

            return _MacroLoader(mod)

        except Exception as e:
            print("import_hooks.MacroFinder",e)
            #raise e

            traceback.print_exc()
            pass
