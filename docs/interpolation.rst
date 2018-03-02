.. _interpolation:

String Interpolation
--------------------

.. note::

  While this is somewhat of just historical interest as of Python 3.6,
  it was in the original set of macros developed for  Python 2.x and
  it's a good example of MacroPy capabilities.

.. code:: python

  from macropy.string_interp import macros, s

  a, b = 1, 2
  print(s["{a} apple and {b} bananas"])
  # 1 apple and 2 bananas


Unlike the normal string interpolation in Python, MacroPy's string
interpolation allows the programmer to specify the variables to be
interpolated _inline_ inside the string. The macro ``s`` then takes
the string literal:

.. code:: python

  "{a} apple and {b} bananas"


and expands it into the expression:

.. code:: python

  "%s apple and %s bananas" % (a, b)


Which is evaluated at run-time in the local scope, using whatever the
values ``a``  and `b` happen to hold at the time. The contents of the
``{...}`` can be any arbitrary python expression, and is not limited to
variable names:

.. code:: python

  from macropy.string_interp import macros, s
  A = 10
  B = 5
  print(s["{A} + {B} = {A + B}"])
  # 10 + 5 = 15
