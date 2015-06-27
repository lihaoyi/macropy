"""Plumbing related to hooking into the import process, unrelated to MacroPy"""

from __future__ import print_function

import ast
import imp
import inspect
import sys
import traceback
import types

import six

if six.PY3:
    from importlib.machinery import PathFinder


import macropy.core.macros
    
import macropy.activate
import macropy.core.exporters
from macropy.core.util import singleton

class _MacroLoader(object):
    """Performs the loading of a module with macro expansion."""
    def __init__(self, module_name, mod):
        self.mod = mod
        sys.modules[module_name] = mod

    def load_module(self, fullname):
        return self.mod


@singleton
class MacroFinder(object):
    """Loads a module and looks for macros inside, only providing a loader if
    it finds some."""
    def expand_macros(self, source_code, filename):
        """ Parses the source_code and expands the resulting ast. 
        Returns both the compiled ast and new ast. 
        If no macros are found, returns None, None."""
        if not source_code or "macros" not in source_code:
            return None, None

        print('Expand macros in %s' % filename, file=sys.stderr)

        tree = ast.parse(source_code)
        bindings = macropy.core.macros.detect_macros(tree)

        if not bindings: 
            return None, None

        for (p, _) in bindings:
            __import__(p)

        modules = [(sys.modules[p], bind) for (p, bind) in bindings]
        new_tree = macropy.core.macros.expand_entire_ast(tree, source_code, modules)
        # print('Compiling', ast.dump(tree), ast.dump(new_tree), sep='\n')
        return compile(tree, filename, "exec"), new_tree

    def construct_module(self, module_name, file_path):
        mod = types.ModuleType(module_name)
        mod.__package__ = module_name.rpartition('.')[0]
        mod.__file__ = file_path
        mod.__loader__ = _MacroLoader(module_name, mod)
        return mod

    def export(self, code, tree, module_name, file_path):
        try:
            macropy.core.exporters.NullExporter().export_transformed(
                code, tree, module_name, file_path)
        except Exception as e:
            # print("Export failure", e, file=sys.stderr) # TODO
            raise

    def get_source(self, module_name, package_path):
        if six.PY3:
            # try to get the module using a "normal" loader.
            # if we fail here, just let python handle the rest
            original_loader = (PathFinder.find_module(module_name, package_path))
            source_code = original_loader.get_source(module_name)
            file_path = original_loader.path
        else:
            # When this is a package, imp.find_module(...)[0] will be
            # None, and this will raise an AttributeError.
            (file, pathname, description) = imp.find_module(
                module_name.split('.')[-1],
                package_path
            )
            # print('Get source: %s %s %s' % (file, pathname, description))
            source_code = file.read()
            file.close()
            file_path = file.name
        return source_code, file_path

    def find_module(self, module_name, package_path):
        try:
            source_code, file_path = self.get_source(module_name, package_path)
        except (AttributeError, ImportError) as e:
            # When trying to find a package, get_source() will raise
            # an AttributeError, which apparently this try-except is
            # designed to catch.  I don't know what happens after
            # that.
            # print('Failed to get source', e, file=macropy/core/sys.stderr)
            return
        try:
            # try to find already exported module
            # TODO: are these the right arguments?
            module = macropy.core.exporters.NullExporter().find(
                file_path, file_path, "", module_name, package_path)
            if module:
                return _MacroLoader(ast.mod)
            code, tree = self.expand_macros(source_code, file_path)
            if not code: # no macros!
                return
            module = self.construct_module(module_name, file_path)
            exec(code, module.__dict__)
            self.export(code, tree, module_name, file_path)
            return module.__loader__
        except Exception as e:
            # print(
            #     "import_hooks.MacroFinder raised %s at line %s" %
            #     (e, e.__traceback__.tb_lineno),
            #     file=sys.stderr)
            # origin = inspect.trace()[-1][0]
            # print(origin.f_locals, origin.f_lineno, file=sys.stderr)
            # traceback.print_exc()
            raise
