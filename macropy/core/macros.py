import sys
import imp
import inspect
import ast
from ast import *
from util import *
from macropy.core import *

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

class ContextWalker(object):
    def __init__(self, func):
        self.func = func
        self.autorecurse = True

    def walk_children(self, tree, ctx=None):
        aggregates = []
        for field, old_value in list(iter_fields(tree)):
            old_value = getattr(tree, field, None)
            new_value, new_aggregate = self.recurse_real(old_value, ctx)
            aggregates.append(new_aggregate)

            setattr(tree, field, new_value)
        return aggregates

    def recurse(self, tree, ctx=None):
        return self.recurse_real(tree, ctx)

    def recurse_real(self, tree, ctx=None):
        if isinstance(tree, list) and len(tree) > 0:
            x = zip(*map(lambda x: self.recurse_real(x, ctx), tree))
            [trees, aggregates] = x
            return flatten(list(trees)), flatten(aggregates)

        elif isinstance(tree, comprehension):
            aggregates = self.walk_children(tree, ctx)
            return tree, flatten(aggregates)
        elif isinstance(tree, AST):
            tree, new_ctx, aggregate = self.func(tree, ctx)
            if self.autorecurse:
                if type(tree) is list:
                    tree, aggregate2 = self.recurse_real(tree, new_ctx)
                    return tree, flatten(aggregate + aggregate2)
                else:
                    aggregates = self.walk_children(tree, new_ctx)
                    return tree, flatten(aggregate + aggregates)
            else:
                return tree, aggregate
        else:
            return tree, []


class Walker(ContextWalker):
    def __init__(self, func):
        self.autorecurse = True
        self.func = lambda tree, ctx: (func(tree), [], [])

    def recurse(self, tree):
        res, agg = self.recurse_real(tree)

        return res

class _MacroLoader(object):
    def __init__(self, module_name, tree, file_name, required_pkgs):
        self.module_name = module_name
        self.tree = tree
        self.file_name = file_name
        self.required_pkgs = required_pkgs

    def load_module(self, fullname):

        for p in self.required_pkgs:
            __import__(p)

        modules = [sys.modules[p] for p in self.required_pkgs]
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


def _detect_macros(tree):
    required_pkgs = []
    for stmt in tree.body:
        if  (isinstance(stmt, ImportFrom)
                and stmt.names[0].name == 'macros'
                and stmt.names[0].asname is  None):
            required_pkgs.append(stmt.module)
            stmt.names = [alias(name='*', asname=None)]
    return required_pkgs


def _expand_ast(tree, modules):
    def macro_expand(tree):
        for module in [m.macros for m in modules]:

            if (isinstance(tree, With)):
                if (isinstance(tree.context_expr, Name)
                        and tree.context_expr.id in module.block_registry):
                    return module.block_registry[tree.context_expr.id](tree), True

                if (isinstance(tree.context_expr, Call)
                        and isinstance(tree.context_expr.func, Name)
                        and tree.context_expr.func.id in module.block_registry):
                    the_macro = module.block_registry[tree.context_expr.func.id]

                    return the_macro(tree, *(tree.context_expr.args)), True

            if  (isinstance(tree, BinOp)
                    and type(tree.left) is Name
                    and type(tree.op) is Mod
                    and tree.left.id in module.expr_registry):

                return module.expr_registry[tree.left.id](tree.right), True

            if  ((isinstance(tree, ClassDef) or isinstance(tree, FunctionDef))
                    and len(tree.decorator_list) == 1
                    and tree.decorator_list[0]
                    and type(tree.decorator_list[0]) is Name
                    and tree.decorator_list[0].id in module.decorator_registry):

                return module.decorator_registry[tree.decorator_list[0].id](tree), True

        return tree, False

    @Walker
    def macro_searcher(tree):
        modified = True
        while modified:
            tree, modified = macro_expand(tree)
        return tree

    tree = macro_searcher.recurse(tree)
    return tree


@singleton
class _MacroFinder(object):
    def find_module(self, module_name, package_path):
        try:
            (file, pathname, description) = imp.find_module(module_name.split('.')[-1], package_path)
            txt = file.read()
            tree = ast.parse(txt)
            required_pkgs = _detect_macros(tree)
            if required_pkgs == []: return
            else: return _MacroLoader(module_name, tree, file.name, required_pkgs)
        except Exception, e:
            pass


sys.meta_path.append(_MacroFinder)
