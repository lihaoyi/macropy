from __future__ import absolute_import

import macropy.activate
import unittest


def test_suite(suites=[], cases=[]):
    new_suites = [x.Tests for x in suites]
    new_cases = [unittest.makeSuite(x.Tests) for x in cases]
    return unittest.TestSuite(new_cases + new_suites)


from . import case_classes
from . import quick_lambda
from . import string_interp
from . import tracing
from . import peg
import macropy.experimental.test
import macropy.core.test


Tests = test_suite(cases=[
    case_classes,
    quick_lambda,
    string_interp,
    tracing,
    peg
], suites=[
    macropy.experimental.test,
    macropy.core.test
])
