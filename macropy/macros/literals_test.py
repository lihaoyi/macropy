import unittest

from macropy.core.macros import *
from macropy.core.lift import *
from macropy.macros.string_interp import *
import time

class Tests(unittest.TestCase):
    def test_basic(self):
        assert(bin%1101101 == 109)
        assert(oct%1234567 == 342391)
        assert(hex%DEADBEEF == 3735928559)


    def test_perf(self):
        start_time = time.time()

        for i in xrange(0, 100000):
            assert(bin%1101101 == 109)
            assert(oct%1234567 == 342391)
            assert(hex%DEADBEEF == 3735928559)

        fast_time = time.time() - start_time
        start_time = time.time()


        for i in xrange(0, 100000):
            assert(int(str(1101101), 2) == 109)
            assert(int(str(1234567), 8) == 342391)
            assert(int("DEADBEEF", 16) == 3735928559)


        normal_time = time.time() - start_time

        assert(normal_time / fast_time > 8)