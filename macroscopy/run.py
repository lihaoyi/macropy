import unittest

from macroscopy.core import macros
from macroscopy.core import lift
from macroscopy.core import lift_test
from macroscopy.macros import string_interp

from macroscopy.macros import string_interp_test
from macroscopy.macros import tracing
from macroscopy.macros import tracing_test

runner = unittest.TextTestRunner()
def run(x):
    runner.run(unittest.TestLoader().loadTestsFromTestCase(x))


run(lift_test.Tests)

run(string_interp_test.Tests)

run(tracing_test.Tests)
