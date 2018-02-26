# -*- coding: utf-8 -*-

import unittest
from macropy.test import test_suite


class Cases:
    class Tests(unittest.TestCase):
        def test_exact_src(self):
            from . import exact_src
            assert exact_src.run0() == "1 * max(1, 2, 3)"
            assert exact_src.run1() == """1 * max((1,'2',"3"))"""
            assert exact_src.run_block() == """
print("omg")
print("wtf")
if 1:
    print('omg')
else:
    import math
    math.acos(0.123)
            """.strip()

        def test_gen_sym(self):
            from . import gen_sym
            gen_sym.run() == 10

        def test_failure(self):
            from macropy.core.failure import MacroExpansionError
            from . import failure
            with self.assertRaises(MacroExpansionError) as ce:
                failure.run1()

            msg = str(ce.exception)
            # TODO: changed the behavior of this test by improving
            # tracebacks for errors.

            # this should contain at least two "i am a cow" and a
            # bunch of stack trace
            assert len(msg.splitlines()) >= 3, msg
            assert msg.rfind("i am a cow") != msg.find("i am a cow")

            # this one should only cotain the "i am a cow" message and
            # nothing else
            with self.assertRaises(MacroExpansionError) as ce:
                failure.run2()
            assert str(ce.exception) == "i am a cow"

            # with self.assertRaises(Exception) as ce:
            with self.assertRaises(MacroExpansionError):
                failure.run3()

            # with self.assertRaises(Exception) as ce:
            with self.assertRaises(MacroExpansionError):
                failure.run4()


from . import quotes
from . import unparse
from . import walkers
from . import macros
from . import hquotes
from . import exporters
from . import analysis
Tests = test_suite(cases = [
    quotes,
    unparse,
    walkers,
    macros,
    Cases,
    hquotes,
#    exporters,
    analysis
])
