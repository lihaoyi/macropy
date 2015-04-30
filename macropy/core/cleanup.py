"""Filters used to touch up the not-quite-perfect ASTs that we allow macros
to return."""


# Imports added by remove_from_imports.

import ast
import _ast



from macropy.core.util import register
from .macros import filters
from .walkers import Walker


@register(filters)
def fix_ctx(tree, **kw):
    return ast_ctx_fixer.recurse(tree, ctx=_ast.Load())


@Walker
def ast_ctx_fixer(tree, stop, set_ctx, set_ctx_for, **kw):
    ctx = kw.get("ctx", None)
    """Fix any missing `ctx` attributes within an AST; allows you to build
    your ASTs without caring about that stuff and just filling it in later."""
    if "ctx" in type(tree)._fields and (not hasattr(tree, "ctx") or tree.ctx is None):
        tree.ctx = ctx

    if type(tree) is _ast.arguments:
        set_ctx_for(tree.args, ctx=_ast.Param())
        set_ctx_for(tree.defaults, ctx=_ast.Load())

    if type(tree) is _ast.AugAssign:
        set_ctx_for(tree.target, ctx=_ast.AugStore())
        set_ctx_for(tree.value, ctx=_ast.AugLoad())

    if type(tree) is _ast.Attribute:
        set_ctx_for(tree.value, ctx=_ast.Load())

    if type(tree) is _ast.Assign:
        set_ctx_for(tree.targets, ctx=_ast.Store())
        set_ctx_for(tree.value, ctx=_ast.Load())

    if type(tree) is _ast.Delete:
        set_ctx_for(tree.targets, ctx=_ast.Del())



@register(filters)
def fill_line_numbers(tree, lineno, col_offset, **kw):
    """Fill in line numbers somewhat more cleverly than the
    ast.fix_missing_locations method, which doesn't take into account the
    fact that line numbers are monotonically increasing down lists of AST
    nodes."""
    if type(tree) is list:
        for sub in tree:
            if isinstance(sub, _ast.AST) \
                    and hasattr(sub, "lineno") \
                    and hasattr(sub, "col_offset") \
                    and (sub.lineno, sub.col_offset) > (lineno, col_offset):

                lineno = sub.lineno
                col_offset = sub.col_offset

            fill_line_numbers(sub, lineno, col_offset)
    elif isinstance(tree, _ast.AST):
        if not (hasattr(tree, "lineno") and hasattr(tree, "col_offset")):
            tree.lineno = lineno
            tree.col_offset = col_offset
        for name, sub in ast.iter_fields(tree):
            fill_line_numbers(sub, tree.lineno, tree.col_offset)

    return tree

