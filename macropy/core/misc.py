from macropy.core import *
from ast import *
from walkers import Walker


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
        for name, sub in iter_fields(tree):
            fill_line_numbers(sub, tree.lineno, tree.col_offset)

@Walker
def ast_ctx_fixer(tree, ctx, stop, **kw):
    """Fix any missing `ctx` attributes within an AST; allows you to build
    your ASTs without caring about that stuff and just filling it in later."""
    if "ctx" in type(tree)._fields and not hasattr(tree, "ctx"):

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

def linear_index(line_lengths, lineno, col_offset):
    prev_length = sum(line_lengths[:lineno-1]) + lineno-2
    out = prev_length + col_offset + 1
    return out

@Walker
def indexer(tree, collect, **kw):
    try:
        unparse_ast(tree)
        collect((tree.lineno, tree.col_offset))
    except Exception, e:
        pass

_transforms = {
    GeneratorExp: "(%s)",
    ListComp: "[%s]",
    SetComp: "{%s}",
    DictComp: "{%s}"
}

def src_for(tree, src, indexes, line_lengths):
    all_child_pos = sorted(indexer.collect(tree))
    start_index = linear_index(line_lengths(), *all_child_pos[0])

    last_child_index = linear_index(line_lengths(), *all_child_pos[-1])

    first_successor_index = indexes()[min(indexes().index(last_child_index)+1, len(indexes())-1)]

    for end_index in range(last_child_index, first_successor_index+1):

        prelim = src[start_index:end_index]
        prelim = _transforms.get(type(tree), "%s") % prelim


        if isinstance(tree, stmt):
            prelim = prelim.replace("\n" + " " * tree.col_offset, "\n")

        if isinstance(tree, list):
            prelim = prelim.replace("\n" + " " * tree[0].col_offset, "\n")

        try:
            if isinstance(tree, expr):
                x = "(" + prelim + ")"
            else:
                x = prelim
            import ast
            parsed = ast.parse(x)
            if unparse_ast(parsed).strip() == unparse_ast(tree).strip():
                return prelim

        except SyntaxError as e:
            pass
    raise Exception("Can't find working source")

