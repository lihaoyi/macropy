import unittest

from macropy.macros2.tracing import macros, trace, log, require

result = []

def log(x):
    result.append(x)
    pass


class Tests(unittest.TestCase):

        def test_basic(self):

            log%(1 + 2)
            log%("omg" * 3)

            assert(result[-2:] == [
                "1 + 2 -> 3",
                "\"omg\" * 3 -> 'omgomgomg'"
            ])

        def test_combo(self):

            trace%(1 + 2 + 3 + 4)

            assert(result[-3:] == [
                "1 + 2 -> 3",
                "1 + 2 + 3 -> 6",
                "1 + 2 + 3 + 4 -> 10"
            ])

        def test_fancy(self):
            trace%([len(x)*3 for x in ['omg', 'wtf', 'b' * 2 + 'q', 'lo' * 3 + 'l']])

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
            trace%sum([sum([1, 2, 3]), min(4, 5, 6), max(7, 8, 9)])
            assert(result[-5:] == [
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

            assert("\n".join(result[-16:]).strip() == """
evens = []
odds = []
for n in range(0, 2):
    if n / 2 == n // 2:
        evens += [n]
    else:
        odds += [n]
range(0, 2) -> [0, 1]
if n / 2 == n // 2:
    evens += [n]
else:
    odds += [n]
n / 2 -> 0
n // 2 -> 0
n / 2 == n // 2 -> True
evens += [n]
[n] -> [0]
if n / 2 == n // 2:
    evens += [n]
else:
    odds += [n]
n / 2 -> 0
n // 2 -> 0
n / 2 == n // 2 -> True
evens += [n]
[n] -> [1]
            """.strip())

        def test_require(self):
            with self.assertRaises(AssertionError) as cm:
                require%(1 == 10)

            assert cm.exception.message == "Require Failed\n1 == 10 -> False"

            require%(1 == 1)

            with self.assertRaises(AssertionError) as cm:
                require%(3**2 + 4**2 != 5**2)


            require%(3**2 + 4**2 == 5**2)

        def test_require_block(self):
            with self.assertRaises(AssertionError) as cm:
                a = 10
                b = 2
                with require:
                    a > 5
                    a * b == 20
                    a < 2
            assert cm.exception.message == "Require Failed\na < 2 -> False"
