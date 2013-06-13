import unittest
import macropy.core.macros
#import scratch

runner = unittest.TextTestRunner()
def run(x):
    runner.run(unittest.TestLoader().loadTestsFromTestCase(x))

from macropy.experimental.test import tco_test
run(tco_test.Tests)

from macropy.experimental.test import pyxl_strings
run(pyxl_strings.Tests)

# this one creates a sqlite database to run, so may take a while
from macropy.experimental.test import pinq
run(pinq.Tests)

# this one needs chromedriver in order to run the javascript using Selenium
# from macropy.experimental.test import js_snippets
# run(js_snippets.Tests)
