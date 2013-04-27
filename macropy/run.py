import unittest
import macropy.core.macros

runner = unittest.TextTestRunner()
def run(x):
    runner.run(unittest.TestLoader().loadTestsFromTestCase(x))


from macropy.core import lift_test
run(lift_test.Tests)

from macropy.macros import literals_test
run(literals_test.Tests)

from macropy.macros import string_interp_test
run(string_interp_test.Tests)

from macropy.macros2 import tracing_test
run(tracing_test.Tests)

from macropy.macros import linq_test
run(linq_test.Tests)

from macropy.macros import quicklambda_test
run(quicklambda_test.Tests)

from macropy.macros import adt_test
run(adt_test.Tests)


from macropy.macros2 import peg_test

run(peg_test.Tests)
