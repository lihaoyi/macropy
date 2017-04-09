from macropy.test import test_suite
# Everything here but pyxl_snippets is commented out in Python 2.7.
# pinq and tco are definitively broken.  I haven't tested
# pyxl_snippets.
# import js_snippets
from . import pattern
# import pinq
# import pyxl_snippets
# import tco

Tests = test_suite(cases = [
    # js_snippets,
    pattern,
    # pinq,
    # pyxl_snippets,
    # tco
])
