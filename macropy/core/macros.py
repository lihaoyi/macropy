import sys
import imp
import inspect
import ast
from ast import *
from macropy.core.core import *
from util import *


class Macros(object):
    def __init__(self):
        self.expr_registry = {}
        self.decorator_registry = {}
        self.block_registry = {}

    def expr(self, f):
        self.expr_registry[f.func_name] = f

    def decorator(self, f):
        self.decorator_registry[f.func_name] = f

    def block(self, f):
        self.block_registry[f.func_name] = f


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


class _MacroLoader(object):
    def __init__(self, module_name, tree, file_name):
        self.module_name = module_name
        self.tree = tree
        self.file_name = file_name

    def load_module(self, fullname):
        required_pkgs = _detect_macros(self.tree)
        for p in required_pkgs:
            __import__(p)

        modules = [sys.modules[p] for p in required_pkgs]
        tree = _expand_ast(self.tree, modules)

        code = unparse_ast(tree)

        ispkg = False
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = []
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        exec compile(code, self.file_name, "exec") in  mod.__dict__
        return mod


def _detect_macros(node):
    required_pkgs = []
    for stmt in node.body:
        if  (isinstance(stmt, ImportFrom)
                and stmt.names[0].name == 'macros'
                and stmt.names[0].asname is  None):

            required_pkgs.append(stmt.module)

    return required_pkgs


def _expand_ast(node, modules):
    def macro_expand(node):
        for module in [m.macros for m in modules]:

            if (isinstance(node, With)):
                if (isinstance(node.context_expr, Name)
                        and node.context_expr.id in module.block_registry):
                    return module.block_registry[node.context_expr.id](node), True

# When passing arguments to a macro.  TODO arity-checking?
                if (isinstance(node.context_expr, Call)
                        and isinstance(node.context_expr.func, Name)
                        and node.context_expr.func.id in module.block_registry):
                    the_macro = module.block_registry[node.context_expr.func.id]

                    return the_macro(node, *(node.context_expr.args)), True

            if  (isinstance(node, BinOp)
                    and type(node.left) is Name
                    and type(node.op) is Mod
                    and node.left.id in module.expr_registry):

                return module.expr_registry[node.left.id](node.right), True

            if  (isinstance(node, ClassDef)
                    and len(node.decorator_list) == 1
                    and node.decorator_list[0]
                    and type(node.decorator_list[0]) is Name
                    and node.decorator_list[0].id in module.decorator_registry):

                return module.decorator_registry[node.decorator_list[0].id](node), True

        return node, False

    @Walker
    def macro_searcher(node):
        modified = True
        while modified:
            node, modified = macro_expand(node)
        return node

    node = macro_searcher.recurse(node)
    return node


@singleton
class _MacroFinder(object):
    def find_module(self, module_name, package_path):
        try:
            (file, pathname, description) = imp.find_module(module_name.split('.')[-1], package_path)
            txt = file.read()
            tree = ast.parse(txt)
            if _detect_macros(tree) == []: return
            else: return _MacroLoader(module_name, tree, file.name)
        except Exception, e:
            pass


sys.meta_path.append(_MacroFinder)
