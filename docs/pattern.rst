.. _pattern:

Pattern Matching
----------------

.. code:: python

  from macropy.case_classes import macros, case
  from macropy.experimental.pattern import macros, switch

  @case
  class Nil():
      pass

  @case
  class Cons(x, xs):
      pass

  def reduce(op, my_list):
      with switch(my_list):
          if Cons(x, Nil()):
              return x
          elif Cons(x, xs):
              return op(x, reduce(op, xs))

  print(reduce(lambda a, b: a + b, Cons(1, Cons(2, Cons(4, Nil())))))
  # 7
  print(reduce(lambda a, b: a * b, Cons(1, Cons(3, Cons(5, Nil())))))
  # 15
  print(reduce(Nil(), lambda a, b: a * b))
  # None


Pattern matching allows you to quickly check a variable against a
series of possibilities, sort of like a `switch statement
<http://en.wikipedia.org/wiki/Switch_statement>`_ on steroids. Unlike
a switch statement in other languages (Java, C++), the ``switch`` macro
allows you to match against the *inside* of a pattern: in this case,
not just that ``my_list`` is a ``Cons`` object, but also that the ``xs``
member of ``my_list`` is a ``Nil`` object. This can be nested arbitrarily
deep, and allows you to easily check if a data-structure has a
particular "shape" that you are expecting. Out of convenience, the
value of the leaf nodes in the pattern are bound to local variables,
so you can immediately use ``x`` and ``xs`` inside the body of the
if-statement without having to extract it (again) from ``my_list``.

The ``reduce`` function above (an simple, cons-list specific
implementation of `reduce
<http://docs.python.org/2/library/functions.html#reduce>`_) takes a
Cons list (defined using `case_classes`:ref:) and quickly
checks if it either a ``Cons`` with a ``Nil`` right hand side, or a ``Cons``
with something else. This is converted (roughly) into:

.. code:: python

  def reduce(my_list, op):
      if isinstance(my_list, Cons) and isinstance(my_list.xs, Nil):
          x = my_list.x
          return x
      elif isinstance(my_list, Cons):
          x = my_list.x
          xs = my_list.xs
          return op(x, reduce(xs, op))


Which is significantly messier to write, with all the ``isinstance``
checks cluttering up the code and having to manually extract the
values you need from ``my_list`` after the ``isinstance`` checks have
passed.

Another common use case for pattern matching is working with tree
structures, like ASTs. This macro is a stylized version of the MacroPy
code to identify ``with ...:`` macros:

.. code:: python

  def expand_macros(node):
      with switch(node):
          if With(Name(name)):
              return handle(name)
          else:
              return node


Compare it to the same code written manually using if-elses:

.. code:: python

  def expand_macros(node):
      if isinstance(node, With) \
              and isinstance(node.context_expr, Name) \
              and node.context_expr.id in macros.block_registry:
          name = node.context_expr.id

              return handle(name)
      else:
          return node


As you can see, matching against ``With(Name(name))`` is a quick and
easy way of checking that the value in ``node`` matches a particular
shape, and is much less cumbersome than a series of conditionals.

It is also possible to use pattern matching outside of a ``switch``, by
using the ``patterns`` macro. Within ``patterns``, any left shift (``<<``)
statement attempts to match the value on the right to the pattern on
the left, allowing nested matches and binding variables as described
earlier.

.. code:: python

  from macropy.experimental.pattern import macros, patterns
  from macropy.case_classes import macros, case

  @case
  class Rect(p1, p2): pass

  @case
  class Line(p1, p2): pass

  @case
  class Point(x, y): pass

  def area(rect):
      with patterns:
          Rect(Point(x1, y1), Point(x2, y2)) << rect
          return (x2 - x1) * (y2 - y1)

  print(area(Rect(Point(1, 1), Point(3, 3)))) # 4


If the match fails, a ``PatternMatchException`` will be thrown.

.. code:: python

  print(area(Line(Point(1, 1), Point(3, 3))))
  # macropy.macros.pattern.PatternMatchException: Matchee should be of type <class 'scratch.Rect'>


Class Matching Details
~~~~~~~~~~~~~~~~~~~~~~

When you pattern match ``Foo(x, y)`` against a value ``Foo(3, 4)``, what
happens behind the scenes is that the constructor of ``Foo`` is
inspected.  We may find that it takes two parameters ``a`` and ``b``.  We
assume that the constructor then contains lines like: ```python self.a
= a self.b = b ``` We don't have access to the source of Foo, so this
is the best we can do.  Then ``Foo(x, y) << Foo(3, 4)`` is transformed
roughly into

.. code:: python

  tmp = Foo(3,4)
  tmp_matcher = ClassMatcher(Foo, [NameMatcher('x'), NameMatcher('y')])
  tmp_matcher.match(tmp)
  x = tmp_matcher.getVar('x')
  y = tmp_matcher.getVar('y')


In some cases, constructors will not be so standard.  In this case, we
can use keyword arguments to pattern match against named fields.  For
example, an equivalent to the above which doesn't rely on the specific
implementation of th constructor is ``Foo(a=x, b=y) << Foo(3, 4)``.
Here the semantics are that the field ``a`` is extracted from ``Foo(3,4)``
to be matched against the simple pattern ``x``.  We could also replace
``x`` with a more complex pattern, as in ``Foo(a=Bar(z), b=y) <<
Foo(Bar(2), 4)``.


Custom Patterns
~~~~~~~~~~~~~~~

It is also possible to completely override the way in which a pattern
is matched by defining an ``__unapply__`` class method of the class
which you are pattern matching.  The 'class' need not actually be the
type of the matched object, as in the following example borrowed from
Scala.  The ``__unapply__`` method takes as arguments the value being
matched, as well as a list of keywords.

The method should then return a tuple of a list of positional matches,
and a dictionary of the keyword matches.

.. code:: python

  class Twice(object):
      @classmethod
      def __unapply__(clazz, x, kw_keys):
          if not isinstance(x, int) or x % 2 != 0:
              raise PatternMatchException()
          else:
              return ([x/2], {})

  with patterns:
      Twice(n) << 8
      print(n)   # 4
