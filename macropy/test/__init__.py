import macropy.activate
import unittest


def test_suite(suites=[], cases=[]):
    new_suites = [x.Tests for x in suites]
    new_cases = [unittest.makeSuite(x.Tests) for x in cases]
    return unittest.TestSuite(new_cases + new_suites)


import case_classes
import quick_lambda
import string_interp
import tracing
#import macropy.experimental.test
#import macropy.core.test
Tests = test_suite(cases=[
    case_classes,
#    quick_lambda,
 #   string_interp,
  #  tracing
], suites=[
   # macropy.experimental.test,
    #macropy.core.test
])

