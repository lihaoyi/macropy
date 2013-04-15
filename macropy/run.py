import unittest

from macropy.core import macros
from macropy.core import lift
from macropy.core import lift_test
from macropy.macros import literals
from macropy.macros import literals_test
from macropy.macros import string_interp
from macropy.macros import string_interp_test
from macropy.macros import tracing
from macropy.macros import tracing_test

runner = unittest.TextTestRunner()
def run(x):
    runner.run(unittest.TestLoader().loadTestsFromTestCase(x))


run(lift_test.Tests)

run(literals_test.Tests)

run(string_interp_test.Tests)

run(tracing_test.Tests)

def match(x): return lambda y: y

x = 10



