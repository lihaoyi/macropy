

# Imports added by remove_from_imports.

import macropy.core
import _ast
import macropy.core.walkers

import unittest

from macropy.core.quotes import macros, q, u

class Tests(unittest.TestCase):
    def test_transform(self):
        tree = macropy.core.parse_expr('(1 + 2) * "3" + ("4" + "5") * 6')
        goal = macropy.core.parse_expr('((("1" * "2") + 3) * ((4 * 5) + "6"))')

        @macropy.core.walkers.Walker
        def transform(tree, **kw):
            if type(tree) is _ast.Num:
                return _ast.Str(s = str(tree.n))
            if type(tree) is _ast.Str:
                return _ast.Num(n = int(tree.s))
            if type(tree) is _ast.BinOp and type(tree.op) is _ast.Mult:
                return _ast.BinOp(tree.left, _ast.Add(), tree.right)
            if type(tree) is _ast.BinOp and type(tree.op) is _ast.Add:
                return _ast.BinOp(tree.left, _ast.Mult(), tree.right)

        assert macropy.core.unparse(transform.recurse(tree)) == macropy.core.unparse(goal)

    def test_collect(self):

        tree = macropy.core.parse_expr('(((1 + 2) + (3 + 4)) + ((5 + 6) + (7 + 8)))')
        total = [0]
        @macropy.core.walkers.Walker
        def sum(tree, collect, **kw):
            if type(tree) is _ast.Num:
                total[0] = total[0] + tree.n
                return collect(tree.n)

        tree, collected = sum.recurse_collect(tree)
        assert total[0] == 36
        assert collected == [1, 2, 3, 4, 5, 6, 7, 8]

        collected = sum.collect(tree)
        assert collected == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_ctx(self):
        tree = macropy.core.parse_expr('(1 + (2 + (3 + (4 + (5)))))')

        @macropy.core.walkers.Walker
        def deepen(tree, ctx, set_ctx, **kw):
            if type(tree) is _ast.Num:
                tree.n = tree.n + ctx
            else:
                return set_ctx(ctx=ctx + 1)

        new_tree = deepen.recurse(tree, ctx=0)
        goal = macropy.core.parse_expr('(2 + (4 + (6 + (8 + 9))))')
        assert macropy.core.unparse(new_tree) == macropy.core.unparse(goal)

    def test_stop(self):
        tree = macropy.core.parse_expr('(1 + 2 * 3 + 4 * (5 + 6) + 7)')
        goal = macropy.core.parse_expr('(0 + 2 * 3 + 4 * (5 + 6) + 0)')

        @macropy.core.walkers.Walker
        def stopper(tree, stop, **kw):
            if type(tree) is _ast.Num:
                tree.n = 0
            if type(tree) is _ast.BinOp and type(tree.op) is _ast.Mult:
                stop()

        new_tree = stopper.recurse(tree)
        assert macropy.core.unparse(goal) == macropy.core.unparse(new_tree)
