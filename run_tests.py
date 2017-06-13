import sys
import unittest
import macropy.activate

import macropy.test

result = unittest.TextTestRunner().run(macropy.test.Tests)
sys.exit(1 if result.errors or result.failures else 0)




