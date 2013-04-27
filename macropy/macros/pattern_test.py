import unittest

from macropy.core.macros import *
from macropy.core.lift import *
from macropy.macros.string_interp import *
from macropy.macros.pattern import macros
from macropy.macros.pattern import *

class Foo(object):
    def __init__(self, x, y):
          self.x = x
          self.y = y


class Bar(object):
    def __init__(self, a):
          self.a = a


class Tests(unittest.TestCase):
    def test_literal_matcher(self):
        matcher = LiteralMatcher(5)
        self.assertTrue(matcher.match(5))
        self.assertFalse(matcher.match(4))

    def test_tuple_matcher(self):
        matcher = TupleMatcher(
                LiteralMatcher(5),
                TupleMatcher(
                    LiteralMatcher(4),
                    LiteralMatcher(5)))
        self.assertEquals(False, matcher.match((5,5)))
        self.assertTrue((True, []), matcher.match((5, (4, 5))))

    def test_class_matcher(self):
        self.assertTrue(
                ClassMatcher(Foo, LiteralMatcher(5),
                    LiteralMatcher(6)).match(Foo(5,6)))
        self.assertFalse(
                ClassMatcher(Foo, LiteralMatcher(5),
                    LiteralMatcher(6)).match(Foo(5,7)))

    def test_disjoint_vars_tuples(self):
        with self.assertRaises(AssertionError):
            TupleMatcher(NameMatcher('x'), NameMatcher('x'))
        TupleMatcher(NameMatcher('y'), NameMatcher('x'))

    def test_disjoint_vars_lists(self):
        with self.assertRaises(AssertionError):
            ListMatcher([NameMatcher('x'), NameMatcher('x')])
        ListMatcher([NameMatcher('y'), NameMatcher('x')])
    
    def test_scary_macros(self):
        with matching:
            print "hello"
        self.assertEquals(3, a)
        self.asserEquals(5, b)

if __name__ == '__main__':
    unittest.main()
