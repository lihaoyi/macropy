import unittest
import macropy.core.macros
#import scratch

runner = unittest.TextTestRunner()
def run(x):
    runner.run(unittest.TestLoader().loadTestsFromTestCase(x))

from macropy.core.test import macros
run(macros.Tests)
