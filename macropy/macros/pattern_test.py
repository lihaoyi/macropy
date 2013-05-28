import unittest

from macropy.macros.pattern import macros


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

    def test_keyword_matching(self):
        foo = Foo(21, 23)
        with patterns:
            Foo(x=x) << foo
            self.assertEquals(21, x)
