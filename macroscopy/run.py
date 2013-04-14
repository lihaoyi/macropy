import unittest

from macroscopy.core import lift
from macroscopy.core import lift_test
from macroscopy.macros import string_interp
from macroscopy.macros import string_interp_test

runner = unittest.TextTestRunner()
def run(x):
    runner.run(unittest.TestLoader().loadTestsFromTestCase(x))


run(lift_test.TestLift)

run(string_interp_test.TestStringInterp)


