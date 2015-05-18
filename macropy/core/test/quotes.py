import ast
import unittest

import macropy.core
from macropy.core.quotes import macros, q, u
from macropy.core import ast_repr

class Tests(unittest.TestCase):

    def test_simple(self):

        a = 10
        b = 2
        data1 = q[1 + u[a + b]]
        data2 = q[1 + (a + b)]

        assert eval(macropy.core.unparse(data1)) == 13
        assert eval(macropy.core.unparse(data2)) == 13
        a = 1
        assert eval(macropy.core.unparse(data1)) == 13
        assert eval(macropy.core.unparse(data2)) == 4


    def test_structured(self):

        a = [1, 2, "omg"]
        b = ["wtf", "bbq"]
        data1 = q[[x for x in u[a + b]]]

        assert(eval(macropy.core.unparse(data1)) == [1, 2, "omg", "wtf", "bbq"])
        b = []
        assert(eval(macropy.core.unparse(data1)) == [1, 2, "omg", "wtf", "bbq"])


    def test_quote_unquote(self):

        x = 1
        y = 2
        a = q[u[x + y]]
        assert(eval(macropy.core.unparse(a)) == 3)
        x = 0
        y = 0
        assert(eval(macropy.core.unparse(a)) == 3)


    def test_unquote_name(self):
        n = "x"
        x = 1
        y = q[name[n] + name[n]]

        assert(eval(macropy.core.unparse(y)) == 2)

    def test_quote_unquote_ast(self):

        a = q[x + y]
        # TODO: This is almost certainly broken but I don't know what
        # it's supposed to do.
        b = q[ast_literal[a] + z]

        x, y, z = 1, 2, 3
        assert(eval(macropy.core.unparse(b)) == 6)
        x, y, z = 1, 3, 9
        assert(eval(macropy.core.unparse(b)) == 13)


    def test_quote_unquote_block(self):

        a = 10
        b = ["a", "b", "c"]
        c = []
        with q as code:
            c.append(a)
            c.append(u[a])
            c.extend(u[b])

        exec(macropy.core.unparse(code))
        assert(c == [10, 10, 'a', 'b', 'c'])
        c = []
        a, b = None, None
        exec(macropy.core.unparse(code))
        assert(c == [None, 10, 'a', 'b', 'c'])

    def test_bad_unquote_error(self):
        with self.assertRaises(TypeError) as ce:
            x = u[10]

        assert str(ce.exception) == (
            "Stub `u` illegally invoked at runtime; "
            "is it used properly within a macro?"
        )
