import unittest
import macropy.activate

import pyxl_snippets

def test_suite(suites=[], cases=[]):
    new_suites = [x.Tests for x in suites]
    new_cases = [unittest.makeSuite(x.Tests) for x in cases]
    return unittest.TestSuite(new_cases + new_suites)

unittest.TextTestRunner().run (
    test_suite (cases= [
        pyxl_snippets] ) )




