import unittest

from macropy.core import macros





runner = unittest.TextTestRunner()
def run(x):
    runner.run(unittest.TestLoader().loadTestsFromTestCase(x))

from macropy.core import lift
from macropy.core import lift_test
run(lift_test.Tests)

from macropy.macros import literals
from macropy.macros import literals_test
run(literals_test.Tests)

from macropy.macros import string_interp
from macropy.macros import string_interp_test
run(string_interp_test.Tests)

from macropy.macros import tracing
from macropy.macros import tracing_test
run(tracing_test.Tests)

from macropy.macros import linq
from macropy.macros import linq_test
run(linq_test.Tests)

from macropy.macros import quicklambda
from macropy.macros import quicklambda_test
run(quicklambda_test.Tests)

