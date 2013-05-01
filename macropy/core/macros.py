import sys
import imp
import ast
from ast import *
from macropy.core.core import *
from util import *


class Placeholder(AST):
    def __repr__(self):
        return "Placeholder()"


def expr_macro(func):
    expr_registry[func.func_name] = func

def decorator_macro(func):
    decorator_registry[func.func_name] = func

def block_macro(func):
    block_registry[func.func_name] = func

def interp_ast(node, values):
    def v(): return values

    @Walker
    def func(node):
        if type(node) is Placeholder:
            val = v().pop(0)
            if isinstance(val, AST):
                return val
            else:
                x = (val)
                return x
        else:
            return node

    x = func.recurse(node)
    return x


class Walker(object):
    def __init__(self, func, autorecurse=True):
        self.func = func
        self.autorecurse = autorecurse

    def walk_children(self, node):
        for field, old_value in list(iter_fields(node)):
            old_value = getattr(node, field, None)
            new_value = self.recurse(old_value)
            setattr(node, field, new_value)

    def recurse(self, node):
        if isinstance(node, list):

            return flatten([
                self.recurse(x)
                for x in node
            ])

        elif isinstance(node, comprehension):
            self.walk_children(node)
            return node
        elif isinstance(node, AST):
            node = self.func(node)
            if self.autorecurse:
                if type(node) is list:
                    return self.recurse(node)
                else:
                    self.walk_children(node)
                    return node
            else:
                return node
        else:
            return node


expr_registry = {}
block_registry = {}
decorator_registry = {}


class MacroLoader(object):
    def __init__(self, module_name, tree, file_name):
        self.module_name = module_name
        self.tree = tree
        self.file_name = file_name

    def load_module(self, fullname):
        required_pkgs, found_macros = detect_macros(self.tree)

        for pkg in required_pkgs:
            __import__(pkg)

        tree = expand_ast(self.tree)

        code = unparse(tree)
        ispkg = False
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = []
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        exec(compile(code, self.file_name, "exec"), mod.__dict__)
        return mod


def detect_macros(node):
    required_pkgs = []
    found_macros = {}
    for stmt in node.body:
        if  (isinstance(stmt, ImportFrom)
                and stmt.names[0].name == 'macros'
                and stmt.names[0].asname is  None):

            for a in stmt.names[1:]:
                found_macros[a.asname or a.name] = a.name
            required_pkgs.append(stmt.module)

    return required_pkgs, found_macros


def expand_ast(node):
    modified = [False]
    def macro_expand(node):
        if (isinstance(node, With)
                and type(node.context_expr) is Name 
                and node.context_expr.id in block_registry):
            modified[0] = True
            return block_registry[node.context_expr.id](node)

        if  (isinstance(node, BinOp) 
                and type(node.left) is Name 
                and type(node.op) is Mod
                and node.left.id in expr_registry):
            modified[0] = True
            return expr_registry[node.left.id](node.right)

        if  (isinstance(node, ClassDef)
                and len(node.decorator_list) == 1
                and node.decorator_list[0]
                and type(node.decorator_list[0]) is Name
                and node.decorator_list[0].id in decorator_registry):
            modified[0] = True
            return decorator_registry[node.decorator_list[0].id](node)
        modified[0] = False
        return node

    @Walker
    def macro_searcher(node):
        modified[0] = [True]
        while modified[0]:
            node = macro_expand(node)
        return node

    node = macro_searcher.recurse(node)
    return node


@singleton
class MacroFinder(object):
    def find_module(self, module_name, package_path):

        try:
            (file, pathname, description) = imp.find_module(module_name.split('.')[-1], package_path)
            txt = file.read()
            tree = ast.parse(txt)
            if detect_macros(tree) == ([], {}): return
            else: return MacroLoader(module_name, tree, file.name)
        except Exception, e:
            pass


sys.meta_path.append(MacroFinder)
