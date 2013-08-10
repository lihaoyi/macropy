"""Plumbing related to hooking into the import process, unrelated to MacroPy"""

import sys
import ast
import macropy.activate
from .macros import *
import traceback
import imp

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

            modules = [(sys.modules[p], bind) for (p, bind) in bindings]

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
            print("Loading", mod)
            return _MacroLoader(mod)

        except Exception as e:
            print("import_hooks.MacroFinder",e)
            #raise e

            traceback.print_exc()
            pass

import importlib
from importlib.machinery import SourceFileLoader, PathFinder
from types import ModuleType
import importlib.abc

class _MacroLoaderPY3(importlib.abc.Loader):
    """Performs the loading of a module with macro expansion."""
    def __init__(self, mod):
        self.mod = mod
        #print("init, ", mod)

    def load_module(self, fullname):
        #print("!! loading", fullname, self.mod)
        self.mod.__loader__ = self
        sys.modules[fullname] = self.mod
        return self.mod

@singleton
class MacroFinderPY3(importlib.abc.MetaPathFinder):
    def find_module(self, module_name, package_path):
        #loader = importlib.find_loader(module_name, pa ckage_path)
        print(module_name, package_path)
        #loader = SourceFileLoader(module_name, package_path[0])
        try:
            loader = (PathFinder.find_module(module_name, package_path))
            #print(loader)
            source_code = loader.get_source(module_name)
        except:
            return
        print(module_name, source_code)
        if not source_code or "macros" not in source_code:
            return

        tree = ast.parse(source_code)
        bindings = detect_macros(tree)
        if bindings == []:
            return # no macros found, carry on


        # TODO - try to import lazily
        for (p, _) in bindings:
            __import__(p)

        modules = [(sys.modules[p], bind) for (p, bind) in bindings]

        tree = expand_entire_ast(tree, source_code, modules)

        code = compile(tree, loader.path, "exec")

        mod = ModuleType(module_name)
        mod.__package__ = module_name.rpartition('.')[0]
        mod.__file__ = loader.path

        #sys.modules[module_name] = mod

        exec(code, mod.__dict__)
        #print("done!")
        return _MacroLoaderPY3(mod)