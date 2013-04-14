from macroscopy.src import macros
from macroscopy.src import *

from lift_test import *


import unittest

runner = unittest.TextTestRunner()
def run(x):
    runner.run(unittest.TestLoader().loadTestsFromTestCase(x))
print "A"

run(TestLift)
print "B"
import string_interp_test
print "C"
run(string_interp_test.TestStringInterp)


