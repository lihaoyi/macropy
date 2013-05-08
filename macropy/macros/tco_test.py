import unittest
from macropy.macros.tco import macros


class Tests(unittest.TestCase):
    def test_tco_returns(self):
        with tco:
            def fact(n, so_far):
                if n == 0:
                    return so_far
                return fact(n-1, n * so_far)
        fact(10000)
        # if we get here, then we haven't thrown a stack overflow.  success.


if __name__ == '__main__':
    unittest.main()
