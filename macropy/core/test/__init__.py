from macropy.test import test_suite


import quotes
import unparse
import walkers
import macros
import hquotes
import exporters
Tests = test_suite(cases = [
    quotes,
    unparse,
    walkers,
    macros,
    hquotes,
    exporters
])