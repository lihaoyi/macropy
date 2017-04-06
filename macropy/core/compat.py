# -*- coding: utf-8 -*-

import sys

PY3 = sys.version_info >= (3,)
PY34 = sys.version_info >= (3, 4)
PY35 = sys.version_info >= (3, 5)

if PY3:
    string_types = (str,)
else:
    string_types = (str, unicode)
