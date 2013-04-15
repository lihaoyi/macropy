import unittest

from macropy.core.macros import *
from macropy.core.lift import *
from macropy.macros.string_interp import *
from tracing import *


result = []


def log(x):
    result.append(x)
    pass


class Tests(unittest.TestCase):

    def test_basic(self):

        log%(1 + 2)
        log%("omg" * 3)

        assert(result[-2:] == [
            "(1 + 2) -> 3",
            "('omg' * 3) -> 'omgomgomg'"
        ])

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

    def test_function_call(self):
        trace%sum([sum([1, 2, 3]), min(4, 5, 6), max(7, 8, 9)])
        assert(result[-6:] == [
            "[1, 2, 3] -> [1, 2, 3]",
            "sum([1, 2, 3]) -> 6",
            "min(4, 5, 6) -> 4",
            "max(7, 8, 9) -> 9",
            "[sum([1, 2, 3]), min(4, 5, 6), max(7, 8, 9)] -> [6, 4, 9]",
            "sum([sum([1, 2, 3]), min(4, 5, 6), max(7, 8, 9)]) -> 19"
        ])

    def test_block_trace(self):

        with trace:
            evens = []
            odds = []

            for n in range(0, 2):
                if n / 2 == n // 2:
                    evens += [n]
                else:
                    odds += [n]


        assert(result[-18:] == [
            "evens = []",
            "[] -> []",
            "odds = []",
            "[] -> []",
            """for n in range(0, 2):
    if ((n / 2) == (n // 2)):
        evens += [n]
    else:
        odds += [n]""",
            "range(0, 2) -> [0, 1]",
            """if ((n / 2) == (n // 2)):
    evens += [n]
else:
    odds += [n]""",
            "(n / 2) -> 0",
            "(n // 2) -> 0",
            "((n / 2) == (n // 2)) -> True",
            "evens += [n]",
             "[n] -> [0]",
            """if ((n / 2) == (n // 2)):
    evens += [n]
else:
    odds += [n]""",
            "(n / 2) -> 0",
            "(n // 2) -> 0",
            "((n / 2) == (n // 2)) -> True",
            "evens += [n]",
             "[n] -> [1]",
        ])

