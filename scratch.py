import macropy.core.quotes as sym3
import macropy.tracing as sym0
import unittest
from ast import *
from macropy.tracing import macros
from macropy.core.quotes import macros, Literal, rename as sym1, Literal as sym2, hygienic_names as hygienic_names
result = []

def log(x):
    result.append(x)
    pass

class Tests(unittest.TestCase):

    def test_block_trace(self):
        log('evens = []')
        evens = []
        log('odds = []')
        odds = []
        log('for n in range(0, 2):\n    if n / 2 == n // 2:\n        evens += [n]\n    else:\n        odds += [n]')
        for n in sym0.macros.registered[0](log, 'range(0, 2)', range(0, 2)):
            log('if n / 2 == n // 2:\n    evens += [n]\nelse:\n    odds += [n]')
            if sym0.macros.registered[3](log, 'n / 2 == n // 2', (sym0.macros.registered[1](log, 'n / 2', (n / 2)) == sym0.macros.registered[2](log, 'n // 2', (n // 2)))):
                log('evens += [n]')
                evens += sym0.macros.registered[4](log, '[n]', [n])
            else:
                log('odds += [n]')
