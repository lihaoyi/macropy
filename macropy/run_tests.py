import unittest
import macropy.core.macros

runner = unittest.TextTestRunner()
def run(x):
    runner.run(unittest.TestLoader().loadTestsFromTestCase(x))

from macropy import core_tests
run(core_tests.Tests)

from macropy.core import lift_test
run(lift_test.Tests)

from macropy.macros import string_interp_test
run(string_interp_test.Tests)

from macropy.macros2 import tracing_test
run(tracing_test.Tests)

from macropy.macros import quicklambda_test
run(quicklambda_test.Tests)

from macropy.macros import pattern_test
run(pattern_test.Tests)

from macropy.macros import adt_test
run(adt_test.Tests)

from macropy.macros2 import peg_test
run(peg_test.Tests)

from macropy.macros2 import pyxl_strings_test
run(pyxl_strings_test.Tests)

from macropy.macros import tco_test
run(tco_test.Tests)

# this one creates a sqlite database to run, so may take a while
from macropy.macros2 import linq_test
run(linq_test.Tests)
#
# # this one needs chromedriver in order to run the javascript using Selenium
from macropy.macros2 import javascript_test
run(javascript_test.Tests)
