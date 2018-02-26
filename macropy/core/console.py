# -*- coding: utf-8 -*-
"""Implementation and activation of a basic macro-powered REPL."""

import ast
import code
import importlib
import sys

from .macros import ModuleExpansionContext, detect_macros


class MacroConsole(code.InteractiveConsole):

    def __init__(self, locals=None, filename="<console>"):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.bindings = []

    def runsource(self, source, filename="<input>", symbol="single"):
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            code = ""
            pass

        if code is None:
            # This means it's incomplete
            return True

        try:
            tree = ast.parse(source)
            bindings = detect_macros(tree, '__main__')

            for mod, bind in bindings:
                self.bindings.append((importlib.import_module(mod), bind))

            tree = ModuleExpansionContext(tree, source, self.bindings).expand_macros()

            tree = ast.Interactive(tree.body)
            code = compile(tree, filename, symbol,
                           self.compile.compiler.flags, 1)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            self.showsyntaxerror(filename)
            # This means there's a syntax error
            return False

        self.runcode(code)
        # This means it was successfully compiled; `runcode` takes care of
        # any runtime failures
        return False
