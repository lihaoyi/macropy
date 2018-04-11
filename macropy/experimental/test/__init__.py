# -*- coding: utf-8 -*-
from macropy.test import test_suite
# Everything here but pyxl_snippets is commented out in Python 2.7.
# pinq and tco are definitively broken.  I haven't tested
# pyxl_snippets.
# import js_snippets
from . import pattern
# import pinq
# import pyxl_snippets
# import tco
from macropy.core.compat import PY35


cases = [pattern]

try:
    import sqlalchemy
    from . import pinq
    cases.append(pinq)
except ImportError:
    print('Excluding pinq tests')

if PY35:
    from . import tco
    cases.append(tco)
else:
    print('Exluding tco tests')

Tests = test_suite(cases = cases)
