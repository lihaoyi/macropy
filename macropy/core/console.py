from _ast import Load
import code
import ast
from codeop import CommandCompiler, Compile, _features
import sys
import inspect
from macropy.core.macros import Load, fill_line_numbers, _ast_ctx_fixer, _expand_ast, _detect_macros


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

        required_pkgs = _detect_macros(tree)
        for p in required_pkgs:
            __import__(p)

        self.modules.update(sys.modules[p] for p in required_pkgs)

        tree = _expand_ast(tree, self.modules)

        tree = _ast_ctx_fixer.recurse(tree, Load())

        fill_line_numbers(tree, 0, 0)
        tree = ast.Interactive(tree.body)
        codeob = compile(tree, filename, symbol, self.flags, 1)
        for feature in _features:
            if codeob.co_flags & feature.compiler_flag:
                self.flags |= feature.compiler_flag
        return codeob




MacroConsole().interact("0=[]=====> MacroPy Enabled <=====[]=0")