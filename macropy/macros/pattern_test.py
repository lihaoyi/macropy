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

class Baz(object):
    def __init__(self, b):
        self.b = b


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

        # with matching:
        #    Foo(a, b) << Foo(4, 5)
        #    for i in xrange(10):
        #    
        #    Foo(a,b) << Foo(4,5):

        matcher1 = ClassMatcher(Foo, NameMatcher('a'),
                NameMatcher('b'))
        matcher1.match_value(Foo(4, 5), False)
        a = matcher1.get_var('a')
        b = matcher1.get_var('b')

    def test_disjoint_vars_tuples(self):
        with self.assertRaises(PatternVarConflict):
            TupleMatcher(NameMatcher('x'), NameMatcher('x'))
        TupleMatcher(NameMatcher('y'), NameMatcher('x'))

    def test_disjoint_vars_lists(self):
        with self.assertRaises(PatternVarConflict):
            ListMatcher(NameMatcher('x'), NameMatcher('x'))
        ListMatcher(NameMatcher('y'), NameMatcher('x'))
    
    def test_basic_matching(self):
        with matching:
            Foo(a, b) << Foo(3, 5)
            self.assertEquals(3, a)
            self.assertEquals(5, b)

    def test_compound_matching(self):
        with matching:
            Foo(x, Foo(4, y)) << Foo(2, Foo(4, 7))
            self.assertEquals(2, x)
            self.assertEquals(7, y)
            Foo("hey there", Foo(x, y)) << Foo("hey there", Foo(1, x))
            self.assertEquals(1, x)
            self.assertEquals(2, y)

    def test_match_exceptions(self):
        with self.assertRaises(Exception):
            Foo(x, Foo(4, y)) << Foo(2, 7)
        with self.assertRaises(Exception):
            Foo(x, Foo(4, y)) << Foo(2, Foo(5, 7))
    
    def test_disjoint_varnames_assertion(self):
        with matching:
            with self.assertRaises(PatternVarConflict):
                Foo(x, x) << Foo(3, 4)
            with self.assertRaises(PatternVarConflict):
                Foo(x, Foo(4, x)) << Foo(3, 4)

    def test_boolean_matching(self):
        with matching:
            with self.assertRaises(PatternMatchException):
                Foo(True, x) << Foo(False, 5)
            self.assertTrue(True)
            self.assertFalse(False)

    def test_atomicity(self):
        with matching:
            x = 1
            y = 5
            with self.assertRaises(PatternMatchException):
                (x, (3, y)) << (2, (4, 6))
            self.assertEquals(1, x)
            self.assertEquals(5, y)
            (x, (3, y)) << (2, (3, 6))
            self.assertEquals(2, x)
            self.assertEquals(6, y)

    def test_switch(self):
        with case_switch:
            if Bar(5) << Bar(6):
                self.assertTrue(False)
            else:
                self.assertTrue(True)

    def test_instance_checking(self):
        blah = Baz(5)
        with case_switch:
            if Foo(lol, wat) << blah:
                self.assertTrue(False)
            elif Bar(4) << blah:
                self.assertTrue(False)
            elif Baz(x) << blah:
                self.assertEquals(5, x)



if __name__ == '__main__':
    unittest.main()
