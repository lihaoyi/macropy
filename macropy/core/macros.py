import sys
import imp
import ast
from ast import *
from util import *
from walkers import *


class Macros(object):
    """A registry of macros belonging to a module; used via

    ```python
    macros = Macros()

    @macros.expr()
    def my_macro(tree):
        ...
    ```

    Where the decorators are used to register functions as macros belonging
    to that module.
    """
    def __init__(self):
        self.expr_registry = {}
        self.decorator_registry = {}
        self.block_registry = {}

    def expr(self, inside_out=False):
        def register(f):
            self.expr_registry[f.func_name] = (f, inside_out)
        return register

    def decorator(self, inside_out=False):
        def register(f):
            self.decorator_registry[f.func_name] = (f, inside_out)
        return register

    def block(self, inside_out=False):
        def register(f):
            self.block_registry[f.func_name] = (f, inside_out)
        return register


def fill_line_numbers(tree, lineno, col_offset):
    """Fill in line numbers somewhat more cleverly than the
    ast.fix_missing_locations method, which doesn't take into account the
    fact that line numbers are monotonically increasing down lists of AST
    nodes."""
    if type(tree) is list:
        for sub in tree:
            if isinstance(sub, AST) \
                    and hasattr(sub, "lineno") \
                    and hasattr(sub, "col_offset") \
                    and (sub.lineno, sub.col_offset) > (lineno, col_offset):

                lineno = sub.lineno
                col_offset = sub.col_offset

            fill_line_numbers(sub, lineno, col_offset)
    elif isinstance(tree, AST):
        if not (hasattr(tree, "lineno") and hasattr(tree, "col_offset")):
            tree.lineno = lineno
            tree.col_offset = col_offset
        for name, sub in ast.iter_fields(tree):
            fill_line_numbers(sub, tree.lineno, tree.col_offset)

@Walker
def _ast_ctx_fixer(tree, ctx):
    """Fix any missing `ctx` attributes within an AST; allows you to build
    your ASTs without caring about that stuff and just filling it in later."""
    if "ctx" in type(tree)._fields and not hasattr(tree, "ctx"):
        tree.ctx = ctx

    if type(tree) is arguments:
        for arg in tree.args:
            _ast_ctx_fixer.recurse(arg, Param())
        for default in tree.defaults:
            _ast_ctx_fixer.recurse(default, Load())

        return tree, stop

    if type(tree) is AugAssign:
        _ast_ctx_fixer.recurse(tree.target, AugStore())
        _ast_ctx_fixer.recurse(tree.value, AugLoad())
        return tree, stop

    if type(tree) is Assign:
        for target in tree.targets:
            _ast_ctx_fixer.recurse(target, Store())

        _ast_ctx_fixer.recurse(tree.value, Load())
        return tree, stop

    if type(tree) is Delete:
        for target in tree.targets:
            _ast_ctx_fixer.recurse(target, Del())
        return tree, stop

class _MacroLoader(object):
    """Performs the loading of a module with macro expansion."""
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

        tree = _ast_ctx_fixer.recurse(tree, Load())

        fill_line_numbers(tree, 0, 0)

        ispkg = False
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = []
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        exec compile(tree, self.file_name, "exec") in mod.__dict__
        return mod


def _detect_macros(tree):
    """Look for macros imports within an AST, transforming them and extracting
    the list of macro modules."""
    required_pkgs = []
    for stmt in tree.body:
        if  (isinstance(stmt, ImportFrom)
                and stmt.names[0].name == 'macros'
                and stmt.names[0].asname is  None):
            required_pkgs.append(stmt.module)
            stmt.names = [alias(name='*', asname=None)]
    return required_pkgs


def _expand_ast(tree, modules):
    """Go through an AST, hunting for macro invocations and expanding any that
    are found"""

    def macro_expand(tree):

        for module in [m.macros for m in modules]:

            if (isinstance(tree, With)):
                if (isinstance(tree.context_expr, Name)
                        and tree.context_expr.id in module.block_registry):
                    pos = (tree.lineno, tree.col_offset) if hasattr(tree, "lineno") and hasattr(tree, "col_offset") else None
                    the_macro, inside_out = module.block_registry[
                            tree.context_expr.id]
                    if inside_out:
                        tree.body = macro_expand(tree.body)
                    new_tree = the_macro(tree)
                    if pos:
                        if type(new_tree) is list:
                            (new_tree[0].lineno, new_tree[0].col_offset) = pos
                        else:
                            (new_tree.lineno, new_tree.col_offset) = pos
                    return new_tree, True

                if (isinstance(tree.context_expr, Call)
                        and isinstance(tree.context_expr.func, Name)
                        and tree.context_expr.func.id in module.block_registry):
                    the_macro, inside_out = module.block_registry[
                            tree.context_expr.func.id]
                    if inside_out:
                        tree.body = macro_expand(tree.body)
                    return the_macro(tree, *(tree.context_expr.args)), True

            if  (isinstance(tree, BinOp)
                    and type(tree.left) is Name
                    and type(tree.op) is Mod
                    and tree.left.id in module.expr_registry):
                pos = (tree.lineno, tree.col_offset)
                the_macro, inside_out = module.expr_registry[tree.left.id]
                if inside_out:
                    tree.right = macro_expand(tree.right)
                new_tree = the_macro(tree.right)
                (new_tree.lineno, new_tree.col_offset) = pos
                return new_tree, True

            if  (isinstance(tree, ClassDef) or isinstance(tree, FunctionDef)):
                decorators = tree.decorator_list
                for i in xrange(len(decorators)):
# The usual macro expansion order is first decorator is expanded first, and then
# the rest of the decorators.  However, if the macro says it wants to be
# expanded inside-out, then 
                    if (isinstance(decorators[i], Name) and decorators[i].id in
                        module.decorator_registry):
                        the_macro, inside_out = module.decorator_registry[
                                decorators[i].id]
                        decorator_prefix = decorators[:i]
                        tree.decorator_list = decorators[i+1:]
                        if inside_out:
                            tree, modified  = macro_expand(tree)
                            if not modified:
                                # This means there are no sub-macros, so we can
                                # actually apply the_macro
                                tree = the_macro(tree)
                                tree.decorator_list = (decorator_prefix +
                                        tree.decorator_list)
                            else:
# We need to keep our current macro decorator in the running
                                tree.decorator_list = (decorator_prefix +
                                        [decorators[i]] + tree.decorator_list)
                            return tree, True
                        else:
                            rreturn the_macro(tree,

        return tree, False

    @Walker
    def macro_searcher(tree):
        modified = True
        while modified:
            tree, modified = macro_expand(tree)
        return tree

    tree = macro_searcher.recurse(tree)

    return tree


@sys.meta_path.append
@singleton
class _MacroFinder(object):
    """Loads a module and looks for macros inside, only providing a loader if
    it finds some."""
    def find_module(self, module_name, package_path):
        try:
            (file, pathname, description) = imp.find_module(
                    module_name.split('.')[-1], package_path)
            txt = file.read()
            tree = ast.parse(txt)
            required_pkgs = _detect_macros(tree)
            if required_pkgs == []: return
            else: return _MacroLoader(module_name, tree, file.name, required_pkgs)
        except Exception, e:
            pass

from macropy.core import console
import inspect
if inspect.stack()[-1][1] == '<stdin>':
    console.MacroConsole().interact("0=[]=====> MacroPy Enabled <=====[]=0")
