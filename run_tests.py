import sys
import unittest
import macropy.activate

import macropy.test

res = unittest.TextTestRunner().run(macropy.test.Tests)
sys.exit(len(res.failures))
