import unittest

from macropy.experimental.pattern import macros, _matching, switch, patterns


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


class Screwy(object):
    def __init__(self, a, b):
        self.x = a
        self.y = b


class Tests(unittest.TestCase):

    def test_literal_matcher(self):
        matcher = LiteralMatcher(5)
        self.assertEquals([], matcher.match(5))
        with self.assertRaises(PatternMatchException):
            self.assertFalse(matcher.match(4))

    def test_tuple_matcher(self):
        matcher = TupleMatcher(
                LiteralMatcher(5),
                TupleMatcher(
                    LiteralMatcher(4),
                    LiteralMatcher(5)))
        with self.assertRaises(PatternMatchException):
            matcher.match((5, 5))
        self.assertEquals([], matcher.match((5, (4, 5))))

    def test_class_matcher(self):
        self.assertEquals([],
                ClassMatcher(Foo, [LiteralMatcher(5),
                    LiteralMatcher(6)]).match(Foo(5,6)))
        with self.assertRaises(PatternMatchException):
            ClassMatcher(Foo, [LiteralMatcher(5),
                LiteralMatcher(6)]).match(Foo(5,7))

        matcher1 = ClassMatcher(Foo, [NameMatcher('a'),
                NameMatcher('b')])
        matcher1.match_value(Foo(4, 5))
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
        with _matching:
            Foo(a, b) << Foo(3, 5)
            self.assertEquals(3, a)
            self.assertEquals(5, b)

    def test_compound_matching(self):
        with _matching:
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
        with _matching:
            with self.assertRaises(PatternVarConflict):
                Foo(x, x) << Foo(3, 4)
            with self.assertRaises(PatternVarConflict):
                Foo(x, Foo(4, x)) << Foo(3, 4)

    def test_boolean_matching(self):
        with _matching:
            with self.assertRaises(PatternMatchException):
                Foo(True, x) << Foo(False, 5)
            self.assertTrue(True)
            self.assertFalse(False)

    def test_atomicity(self):
        with _matching:
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
        with switch(Bar(6)):
            if Bar(5):
                self.assertTrue(False)
            else:
                pass

    def test_instance_checking(self):
        blah = Baz(5)
        with switch(blah):
            if Foo(lol, wat):
                self.assertTrue(False)
            elif Bar(4):
                self.assertTrue(False)
            elif Baz(x):
                self.assertEquals(5, x)
            self.assertEquals(8, 1 << 3)

    def test_patterns_macro(self):
        blah = Baz(5)
        with patterns:
            if Foo(lol, wat) << blah:
# this shouldn't happen
                self.assertTrue(False)
            elif Bar(4) << blah:
                self.assertTrue(False)
            elif Baz(x) << blah:
                self.assertEquals(5, x)

    def test_keyword_matching(self):
        foo = Foo(21, 23)
        with patterns:
            Foo(x=x) << foo
            self.assertEquals(21, x)
