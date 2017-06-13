from macropy.test import test_suite
#import js_snippets
#import pattern
#import pinq
cases = []
try:
    import pyxl
except ImportError:
    pass
else:
    import pyxl_snippets
    cases.append(pyxl_snippets)
#import tco_test

Tests = test_suite(cases = cases)
