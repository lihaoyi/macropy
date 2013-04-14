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
    def test_tracing(self):
        with q as code:
            trace%(1 + 2)

        exec to_str(code)

        assert(result[-1] == "(1 + 2) -> 3")



def to_str(txt):
    node = expand_ast(txt)
    return unparse(node)
