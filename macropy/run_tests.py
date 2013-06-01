import unittest
import macropy.core.macros


runner = unittest.TextTestRunner()
def run(x):
    runner.run(unittest.TestLoader().loadTestsFromTestCase(x))


from macropy import core_tests
run(core_tests.Tests)

from macropy.core import lift_test
run(lift_test.Tests)

from macropy.core import walkers_test
run(walkers_test.Tests)

from macropy.macros import string_interp_test
run(string_interp_test.Tests)

from macropy.macros import quicklambda_test
run(quicklambda_test.Tests)

from macropy.macros import adt_test
run(adt_test.Tests)

from macropy.experimental import peg_test
run(peg_test.Tests)

from macropy.experimental import pyxl_strings_test
run(pyxl_strings_test.Tests)

from macropy.experimental import tco_test
run(tco_test.Tests)

from macropy.experimental import pattern_test
run(pattern_test.Tests)

# this one creates a sqlite database to run, so may take a while
from macropy.experimental import linq_test
run(linq_test.Tests)

# this one needs chromedriver in order to run the javascript using Selenium
from macropy.experimental import javascript_test
run(javascript_test.Tests)
