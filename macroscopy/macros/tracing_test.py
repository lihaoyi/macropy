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

        log%(1 + 2)
        log%("omg" * 3)

        assert(result[-2] == "(1 + 2) -> 3")
        assert(result[-1] == "('omg' * 3) -> 'omgomgomg'")

    def test_combo(self):

        trace%(1 + 2 + 3 + 4)

        assert(result[-3:] == [
            "(1 + 2) -> 3",
            "((1 + 2) + 3) -> 6",
            "(((1 + 2) + 3) + 4) -> 10"
        ])
    def test_fancy(self):
        trace%([len(x)*3 for x in ["omg", "wtf", "b" * 2 + "q", "lo" * 3 + "l"]])
        assert(result[-14:] == [
            "('b' * 2) -> 'bb'",
            "(('b' * 2) + 'q') -> 'bbq'",
            "('lo' * 3) -> 'lololo'",
            "(('lo' * 3) + 'l') -> 'lololol'",
            "['omg', 'wtf', (('b' * 2) + 'q'), (('lo' * 3) + 'l')] -> ['omg', 'wtf', 'bbq', 'lololol']",
            "len(x) -> 3",
            "(len(x) * 3) -> 9",
            "len(x) -> 3",
            "(len(x) * 3) -> 9",
            "len(x) -> 3",
            "(len(x) * 3) -> 9",
            "len(x) -> 7",
            "(len(x) * 3) -> 21",
            "[(len(x) * 3) for x in ['omg', 'wtf', (('b' * 2) + 'q'), (('lo' * 3) + 'l')]] -> [9, 9, 9, 21]"
        ])

