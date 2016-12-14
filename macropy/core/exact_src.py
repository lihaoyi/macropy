"""Logic related to lazily performing the computation necessary to finding
the source extent of an AST.

Exposed to each macro as an `exact_src` funciton."""

from macropy.core import unparse
from macropy.core.macros import injected_vars
from ast import *
from macropy.core.util import Lazy, distinct, register
from .walkers import Walker


def linear_index(line_lengths, lineno, col_offset):
    prev_length = sum(line_lengths[:lineno-1]) + lineno-2
    out = prev_length + col_offset + 1
    return out

@Walker
def indexer(tree, collect, **kw):
    try:
        unparse(tree)
        collect((tree.lineno, tree.col_offset))
    except: pass

_transforms = {
    GeneratorExp: "(%s)",
    ListComp: "[%s]",
    SetComp: "{%s}",
    DictComp: "{%s}"
}


@register(injected_vars)
def exact_src(tree, src, **kw):

    def exact_src_imp(tree, src, indexes, line_lengths):
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
                if unparse(parsed).strip() == unparse(tree).strip():
                    return prelim

            except SyntaxError as e:
                pass
        raise ExactSrcException()

    positions = Lazy(lambda: indexer.collect(tree))
    line_lengths = Lazy(lambda: list(map(len, src.split("\n"))))
    indexes = Lazy(lambda: distinct([linear_index(line_lengths(), l, c) for (l, c) in positions()] + [len(src)]))
    return lambda t: exact_src_imp(t, src, indexes, line_lengths)
class ExactSrcException(Exception):
    pass
