import code
import ast
from codeop import CommandCompiler, Compile, _features
import sys

import macropy.core.macros


class MacroConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>"):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.compile = MacroCommandCompiler()


class MacroCommandCompiler(CommandCompiler):
    def __init__(self,):
        CommandCompiler.__init__(self)
        self.compiler = MacroCompile()


class MacroCompile(Compile):
    def __init__(self):
        Compile.__init__(self)
        self.modules = set()
    def __call__(self, source, filename, symbol):
        tree = ast.parse(source)
        required_pkgs = macropy.core.macros._detect_macros(tree)
        for p in required_pkgs:
            __import__(p)

        self.modules.update(sys.modules[p] for p in required_pkgs)

        tree = macropy.core.macros._expand_ast(tree, self.modules)
            
        tree = macropy.core.macros._ast_ctx_fixer.recurse(tree, macropy.core.macros.Load())

        macropy.core.macros.fill_line_numbers(tree, 0, 0)
        tree = ast.Interactive(tree.body)
        codeob = compile(tree, filename, symbol, self.flags, 1)
        for feature in _features:
            if codeob.co_flags & feature.compiler_flag:
                self.flags |= feature.compiler_flag
        return codeob

