# -*- coding: utf-8 -*-
"""Logic related to lazily performing the computation necessary to finding
the source extent of an AST.

Exposed to each macro as an `exact_src` function."""

import ast

from . import unparse
from .macros import injected_vars
from .util import Lazy, distinct, register
from .walkers import Walker


def linear_index(line_lengths, lineno, col_offset):
    prev_length = sum(line_lengths[:lineno-1]) + lineno-2
    out = prev_length + col_offset + 1
    return out


@Walker
def indexer(tree, collect, **kw):
    try:
        # print('Indexer: %s' % ast.dump(tree), file=sys.stderr)
        unparse(tree)
        collect((tree.lineno, tree.col_offset))
    except (AttributeError, KeyError) as e:
        # If this handler gets executed it's because unparse() has
        # failed (it's being used as a poor man's syntax
        # checker). It's important to remember that unparse cannot
        # unparse *any* tree fragment. There are certain fragments,
        # (like an ast.Add without its parent ast.BinOp) that cannot
        # be unparsed alone
        pass
        # print("Failure in exact_src.py", e, file=sys.stderr)
        # raise


_transforms = {
    ast.GeneratorExp: "(%s)",
    ast.ListComp: "[%s]",
    ast.SetComp: "{%s}",
    ast.DictComp: "{%s}"
}


@register(injected_vars)
def exact_src(tree, src, **kw):

    def exact_src_imp(tree, src, indexes, line_lengths):
        all_child_pos = sorted(indexer.collect(tree))
        start_index = linear_index(line_lengths(), *all_child_pos[0])

        last_child_index = linear_index(line_lengths(), *all_child_pos[-1])

        first_successor_index = indexes()[min(indexes().index(last_child_index)+1,
                                              len(indexes())-1)]

        for end_index in range(last_child_index, first_successor_index+1):

            prelim = src[start_index:end_index]
            prelim = _transforms.get(type(tree), "%s") % prelim

            if isinstance(tree, ast.stmt):
                prelim = prelim.replace("\n" + " " * tree.col_offset, "\n")

            if isinstance(tree, list):
                prelim = prelim.replace("\n" + " " * tree[0].col_offset, "\n")

            try:
                if isinstance(tree, ast.expr):
                    x = "(" + prelim + ")"
                else:
                    x = prelim
                parsed = ast.parse(x)
                if unparse(parsed).strip() == unparse(tree).strip():
                    return prelim

            except SyntaxError as e:
                pass
        raise ExactSrcException()

    positions = Lazy(lambda: indexer.collect(tree))
    line_lengths = Lazy(lambda: list(map(len, src.split("\n"))))
    indexes = Lazy(lambda: distinct([linear_index(line_lengths(), l, c)
                                for (l, c) in positions()] + [len(src)]))
    return lambda t: exact_src_imp(t, src, indexes, line_lengths)


class ExactSrcException(Exception):
    pass
