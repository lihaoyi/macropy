from _ast import Load
import code
import ast
from codeop import CommandCompiler, Compile, _features
import sys
import inspect
from macropy.core.macros import process_ast, detect_macros


class MacroConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>"):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.modules = set()

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
            required_pkgs = detect_macros(tree)
            for p in required_pkgs:
                __import__(p)

            self.modules.update(sys.modules[p] for p in required_pkgs)
            tree = process_ast(tree, self.modules)

            tree = ast.Interactive(tree.body)
            code = compile(tree, filename, symbol, self.compile.compiler.flags, 1)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            self.showsyntaxerror(filename)
            # This means there's a syntax error
            return False


        self.runcode(code)
        # This means it was successfully compiled; `runcode` takes care of
        # any runtime failures
        return False

MacroConsole().interact("0=[]=====> MacroPy Enabled <=====[]=0")
