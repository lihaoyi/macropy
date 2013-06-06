import unittest
import macropy.core.macros
#import scratch

runner = unittest.TextTestRunner()
def run(x):
    runner.run(unittest.TestLoader().loadTestsFromTestCase(x))
"""
from macropy.core.test import macros
run(macros.Tests)

from macropy.core.test import quotes
run(quotes.Tests)

from macropy.core.test import unparse_ast
run(unparse_ast.Tests)

from macropy.core.test import walkers
run(walkers.Tests)

from macropy.test import string_interp
run(string_interp.Tests)

from macropy.test import quick_lambda
run(quick_lambda.Tests)

from macropy.test import case_classes
run(case_classes.Tests)

from macropy.test import tracing
run(tracing.Tests)
"""
from macropy.experimental.test import peg
run(peg.Tests)

"""
from macropy.experimental.test import tco_test
run(tco_test.Tests)

from macropy.experimental.test import pattern
run(pattern.Tests)

from macropy.experimental.test import pyxl_strings
run(pyxl_strings.Tests)
"""
"""
# this one creates a sqlite database to run, so may take a while
from macropy.experimental.test import pinq
run(pinq.Tests)

# this one needs chromedriver in order to run the javascript using Selenium
from macropy.experimental.test import js_snippets
run(js_snippets.Tests)
"""