# -*- coding: utf-8 -*-
from macropy.test import test_suite
from macropy.core.compat import PY35

from . import pattern
# This doesn't currently work in MacroPy3 due to a missing dependency
# from . import js_snippets

cases = [pattern]

try:
    import sqlalchemy  # noqa: F401
    from . import pinq
    cases.append(pinq)
except ImportError:
    print('Excluding pinq tests')

if PY35:
    from . import tco
    cases.append(tco)
else:
    print('Exluding tco tests')

try:
    from . import pyxl_snippets
    cases.append(pyxl_snippets)
except RuntimeError:
    print('Excluding pyxl tests')

Tests = test_suite(cases=cases)
