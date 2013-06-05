import unittest


from macropy.string_interp import macros, s


class Tests(unittest.TestCase):
    def test_string_interpolate(self):
        a, b = 1, 2
        c = s["{a} apple and {b} bananas"]
        assert(c == "1 apple and 2 bananas")


    def test_string_interpolate_2(self):
        apple_count = 10
        banana_delta = 4
        c = s["{apple_count} {'apples'} and {apple_count + banana_delta} {''.join(['b', 'a', 'n', 'a', 'n', 'a', 's'])}"]

        assert(c == "10 apples and 14 bananas")
