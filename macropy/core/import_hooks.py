# -*- coding: utf-8 -*-
"""Plumbing related to hooking into the import process, unrelated to
MacroPy"""

import ast
import importlib
from importlib.util import spec_from_loader
import logging
import sys

import macropy.activate

from . import macros  # noqa: F401
from . import exporters  # noqa: F401
from .util import singleton


logger = logging.getLogger(__name__)


class _MacroLoader(object):
    """Performs the loading of a module with macro expansion."""

    def __init__(self, module_name, mod):
        self.mod = mod
        sys.modules[module_name] = mod

    def load_module(self, fullname):
        return self.mod


class MacroLoader:
    """Performs the real module loading in Python 3. the other is still
    there until the export stuff is fixed.
    """

    def __init__(self, nomacro_spec, code, tree):
        self.nomacro_spec = nomacro_spec
        self.code = code
        self.tree = tree

    def create_module(self, spec):
        pass

    def exec_module(self, module):
        exec(self.code, module.__dict__)
        self.export()

    def export(self):
        try:
            macropy.exporter.export_transformed(
                self.code, self.tree, self.nomacro_spec.name,
                self.nomacro_spec.origin)
        except Exception as e:
            raise

    def get_filename(self, fullname):
        return self.nomacro_spec.loader.get_filename(fullname)

    def is_package(self, fullname):
        return self.nomacro_spec.loader.is_package(fullname)


@singleton
class MacroFinder(object):
    """Loads a module and looks for macros inside, only providing a loader
    if it finds some.
    """

    def _find_spec_nomacro(self, fullname, path, target=None):
        """Try to find the original, non macro-expanded module using all the
        remaining meta_path finders. This one is installed by
        ``macropy.activate`` at index 0."""
        spec = None
        for finder in sys.meta_path:
            # when testing with pytest, it installs a finder that for
            # some yet unknown reasons makes macros expansion
            # fail. For now it will just avoid using it and pass to
            # the next one
            if finder is self or 'pytest' in finder.__module__:
                continue
            if hasattr(finder, 'find_spec'):
                spec = finder.find_spec(fullname, path, target=target)
            elif hasattr(finder, 'load_module'):
                spec = spec_from_loader(fullname, finder)
            if spec is not None:
                break
        return spec

    def expand_macros(self, source_code, filename, spec):
        """ Parses the source_code and expands the resulting ast.
        Returns both the compiled ast and new ast.
        If no macros are found, returns None, None."""
        if not source_code or "macros" not in source_code:
            return None, None

        logger.info('Expand macros in %s', filename)

        tree = ast.parse(source_code)
        bindings = macropy.core.macros.detect_macros(tree, spec.name,
                                                     spec.parent,
                                                     spec.name)

        if not bindings:
            return None, None

        modules = []
        for mod, bind in bindings:
            modules.append((importlib.import_module(mod), bind))
        new_tree = macropy.core.macros.ModuleExpansionContext(
            tree, source_code, modules).expand_macros()
        try:
            return compile(tree, filename, "exec"), new_tree
        except Exception:
            logger.exception("Error while compiling file %s", filename)
            raise

    def find_spec(self, fullname, path, target=None):
        spec = self._find_spec_nomacro(fullname, path, target)
        if spec is None or not (hasattr(spec.loader, 'get_source') and
            callable(spec.loader.get_source)):  # noqa: E128
            if fullname != 'org':
                # stdlib pickle.py at line 94 contains a ``from
                # org.python.core for Jython which is always failing,
                # of course
                logging.debug('Failed finding spec for %s', fullname)
            return
        origin = spec.origin
        if origin == 'builtin':
            return
        # # try to find already exported module
        # # TODO: are these the right arguments?
        # # NOTE: This is a noop
        # module = macropy.core.exporters.NullExporter().find(
        #     file_path, file_path, "", module_name, package_path)
        # if module:
        #     return _MacroLoader(ast.mod)
        try:
            source = spec.loader.get_source(fullname)
        except ImportError:
            logging.debug('Loader for %s was unable to find the sources',
                          fullname)
            return
        except Exception:
            logging.exception('Loader for %s raised an error', fullname)
            return
        code, tree = self.expand_macros(source, origin, spec)
        if not code:  # no macros!
            return
        loader = MacroLoader(spec, code, tree)
        return spec_from_loader(fullname, loader)
