import unittest

from macropy.core.macros import *
from macropy.core.lift import *
from macropy.macros.string_interp import *

class Foo(object):
  def __init__(self, x, y):
    self.x = x
    self.y = y

class Bar(object):
  def __init__(self, a):
    self.a = a

class Tests(unittest.TestCase):
  def test_literal_leaves(self):
    foo = Foo([3,4,5], 6)
    with match:
      Foo(a, 6) << foo
      self.assertEquals([3,4,5], a)
      
