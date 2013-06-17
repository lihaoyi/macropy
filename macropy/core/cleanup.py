"""Non-trivial AST operations used in macros.py"""


from ast import *
from macropy.core.util import register
from macros import filters
from walkers import Walker




@register(filters)
def fix_ctx(tree, **kw):
    return ast_ctx_fixer.recurse(tree, Load())



@Walker
def ast_ctx_fixer(tree, ctx, stop, **kw):
    """Fix any missing `ctx` attributes within an AST; allows you to build
    your ASTs without caring about that stuff and just filling it in later."""
    if "ctx" in type(tree)._fields and (not hasattr(tree, "ctx") or tree.ctx is None):

        tree.ctx = ctx

    if type(tree) is arguments:
        for arg in tree.args:
            ast_ctx_fixer.recurse(arg, Param())
        for default in tree.defaults:
            ast_ctx_fixer.recurse(default, Load())
        stop()
        return tree

    if type(tree) is AugAssign:
        ast_ctx_fixer.recurse(tree.target, AugStore())
        ast_ctx_fixer.recurse(tree.value, AugLoad())
        stop()
        return tree

    if type(tree) is Assign:
        for target in tree.targets:
            ast_ctx_fixer.recurse(target, Store())

        ast_ctx_fixer.recurse(tree.value, Load())
        stop()
        return tree

    if type(tree) is Delete:
        for target in tree.targets:
            ast_ctx_fixer.recurse(target, Del())
        stop()
        return tree


@register(filters)
def fill_line_numbers(tree, lineno, col_offset, **kw):
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
        for name, sub in iter_fields(tree):
            fill_line_numbers(sub, tree.lineno, tree.col_offset)

    return tree

