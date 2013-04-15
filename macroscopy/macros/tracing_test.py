import unittest

from macroscopy.core.macros import *
from macroscopy.core.lift import *
from macroscopy.macros.string_interp import *
from tracing import *


result = []
def log(x):
    result.append(x)
    pass


class Tests(unittest.TestCase):
    def test_basic(self):

        with q as code:
            log%(1 + 2)
            log%("omg" * 3)

        print to_str(code)
        exec to_str(code)

        assert(result[-2] == "(1 + 2) -> 3")
        assert(result[-1] == "('omg' * 3) -> 'omgomgomg'")

    def test_fancy(self):

        with q as code:
            trace%(1 + 2 + 3 + 4)

        exec to_str(code)
        print result[-3:]
        assert(result[-3:] == [
            "(1 + 2) -> 3",
            "((1 + 2) + 3) -> 6",
            "(((1 + 2) + 3) + 4) -> 10"
        ])

        def func(x): return x * 3

        with q as code:

            trace%([x for x in [1, 2, 3]])

        print to_str(code)
        exec to_str(code)
        print "================="
        for line in result:
            print line


def to_str(txt):
    node = expand_ast(txt)
    return unparse(node)
