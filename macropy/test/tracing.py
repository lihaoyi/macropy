import ast
import unittest

from macropy.tracing import macros, trace, log, require, show_expanded
from macropy.core.quotes import macros, q
result = []

def log(x):
    result.append(x)


class Tests(unittest.TestCase):

    def test_basic(self):

        log[1 + 2]
        log["omg" * 3]

        assert(result[-2:] == [
            "1 + 2 -> 3",
            "\"omg\" * 3 -> 'omgomgomg'"
        ])

    def test_combo(self):

        trace[1 + 2 + 3 + 4]

        self.assertEqual(result[-3:], [
            "1 + 2 -> 3",
            "1 + 2 + 3 -> 6",
            "1 + 2 + 3 + 4 -> 10"
        ])

    def test_fancy(self):
        trace[[len(x)*3 for x in ['omg', 'wtf', 'b' * 2 + 'q', 'lo' * 3 + 'l']]]

        assert(result[-14:] == [
            "'b' * 2 -> 'bb'",
            "'b' * 2 + 'q' -> 'bbq'",
            "'lo' * 3 -> 'lololo'",
            "'lo' * 3 + 'l' -> 'lololol'",
            "['omg', 'wtf', 'b' * 2 + 'q', 'lo' * 3 + 'l'] -> ['omg', 'wtf', 'bbq', 'lololol']",
            "len(x) -> 3",
            "len(x)*3 -> 9",
            "len(x) -> 3",
            "len(x)*3 -> 9",
            "len(x) -> 3",
            "len(x)*3 -> 9",
            "len(x) -> 7",
            "len(x)*3 -> 21",
            "[len(x)*3 for x in ['omg', 'wtf', 'b' * 2 + 'q', 'lo' * 3 + 'l']] -> [9, 9, 9, 21]"
        ])

    def test_function_call(self):
        trace[sum([sum([1, 2, 3]), min(4, 5, 6), max(7, 8, 9)])]
        assert(result[-5:] == [
            "sum([1, 2, 3]) -> 6",
            "min(4, 5, 6) -> 4",
            "max(7, 8, 9) -> 9",
            "[sum([1, 2, 3]), min(4, 5, 6), max(7, 8, 9)] -> [6, 4, 9]",
            "sum([sum([1, 2, 3]), min(4, 5, 6), max(7, 8, 9)]) -> 19"
        ])


    def test_require(self):
        with self.assertRaises(AssertionError) as cm:
            require[1 == 10]

        assert str(cm.exception) == "Require Failed\n1 == 10 -> False"

        require[1 == 1]

        with self.assertRaises(AssertionError) as cm:
            require[3**2 + 4**2 != 5**2]


        require[3**2 + 4**2 == 5**2]

    def test_require_block(self):
        with self.assertRaises(AssertionError) as cm:
            a = 10
            b = 2
            with require:
                a > 5
                a * b == 20
                a < 2
        assert str(cm.exception) == "Require Failed\na < 2 -> False"


    def test_show_expanded(self):

        from macropy.core import ast_repr
        show_expanded[q[1 + 2]]

        assert ("ast.BinOp(left=ast.Num(n=1), op=ast.Add(), "
                "right=ast.Num(n=2))" in result[-1])

        with show_expanded:
            a = 1
            b = 2
            with q as code:
                return(a + u[b + 1])

        assert result[-3] == '\na = 1'
        assert result[-2] == '\nb = 2'
        self.assertEqual("\ncode = [ast.Return(value=ast.BinOp("
                         "left=ast.Name(id='a'"", ctx=ast.Load()), "
                         "op=ast.Add(), right=ast_repr((b + 1))))]",
                         result[-1])
