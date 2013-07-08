import unittest
import sys
import hq

class Tests(unittest.TestCase):
    def test_hq(self):

        assert hq.run1() == "2x: 1 double 1 double "

        assert hq.run2() == 5

        assert hq.run3() == 6

    def test_error(self):
        with self.assertRaises(TypeError) as ce:
            hq.run_error()

        assert ce.exception.message == (
            "Stub `unhygienic` illegally invoked at runtime; "
            "is it used properly within a macro?"
        )