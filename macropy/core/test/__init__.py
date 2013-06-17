import unittest
from macropy.test import test_suite

import exact_src
import gen_sym
import quotes
import unparse
import walkers
import macros
import hquotes
import exporters

class Cases:
    class Tests(unittest.TestCase):
        def test_exact_src(self):
            assert exact_src.run0() == "1 * max(1, 2, 3)"
            assert exact_src.run1() == """1 * max((1,'2',"3"))"""
            assert exact_src.run_block() == """
print "omg"
print "wtf"
if 1:
    print 'omg'
else:
    import math
    math.acos(0.123)
            """.strip()

        def test_gen_sym(self):
            gen_sym.run() == 10

Tests = test_suite(cases = [
    quotes,
    unparse,
    walkers,
    macros,
    Cases,
    hquotes,
    exporters
])