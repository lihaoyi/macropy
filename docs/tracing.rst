.. _tracing:

Tracing
-------

.. code:: python

  from macropy.tracing import macros, log
  log[1 + 2]
  # 1 + 2 -> 3
  # 3

  log["omg" * 3]
  # ('omg' * 3) -> 'omgomgomg'
  # 'omgomgomg'


Tracing allows you to easily see what is happening inside your
code. Many a time programmers have written code like

.. code:: python

  print("value", value)
  print("sqrt(x)", sqrt(x))


and the ``log()`` macro (shown above) helps remove this duplication by
automatically expanding ``log(1 + 2)`` into ``wrap("(1 + 2)", (1 +
2))``. ``wrap`` then evaluates the expression, printing out the source
code and final value of the computation.

In addition to simple logging, MacroPy provides the ``trace()``
macro. This macro not only logs the source and result of the given
expression, but also the source and result of all sub-expressions
nested within it:

.. code:: python

  from macropy.tracing import macros, trace
  trace[[len(x)*3 for x in ["omg", "wtf", "b" * 2 + "q", "lo" * 3 + "l"]]]
  # "b" * 2 -> 'bb'
  # "b" * 2 + "q" -> 'bbq'
  # "lo" * 3 -> 'lololo'
  # "lo" * 3 + "l" -> 'lololol'
  # ["omg", "wtf", "b" * 2 + "q", "lo" * 3 + "l"] -> ['omg', 'wtf', 'bbq', 'lololol']
  # len(x) -> 3
  # len(x)*3 -> 9
  # len(x) -> 3
  # len(x)*3 -> 9
  # len(x) -> 3
  # len(x)*3 -> 9
  # len(x) -> 7
  # len(x)*3 -> 21
  # [len(x)*3 for x in ["omg", "wtf", "b" * 2 + "q", "lo" * 3 + "l"]] -> [9, 9, 9, 21]
  # [9, 9, 9, 21]


As you can see, ``trace`` logs the source and value of all
sub-expressions that get evaluated in the course of evaluating the
list comprehension.

Lastly, ``trace`` can be used as a block macro:


.. code:: python

  from macropy.tracing import macros, trace
  with trace:
      sum = 0
      for i in range(0, 5):
          sum = sum + 5

  # sum = 0
  # for i in range(0, 5):
  #     sum = sum + 5
  # range(0, 5) -> [0, 1, 2, 3, 4]
  # sum = sum + 5
  # sum + 5 -> 5
  # sum = sum + 5
  # sum + 5 -> 10
  # sum = sum + 5
  # sum + 5 -> 15
  # sum = sum + 5
  # sum + 5 -> 20
  # sum = sum + 5
  # sum + 5 -> 25


Used this way, ``trace`` will print out the source code of every
*statement* that gets executed, in addition to tracing the evaluation
of any expressions within those statements.

Apart from simply printing out the traces, you can also redirect the
traces wherever you want by having a ``log()`` function in scope:

.. code:: python

  result = []

  def log(x):
      result.append(x)


The tracer uses whatever ``log()`` function it finds, falling back on
printing only if none exists. Instead of printing, this ``log()``
function appends the traces to a list, and is used in our unit tests.

We think that tracing is an extremely useful macro. For debugging what
is happening, for teaching newbies how evaluation of expressions
works, or for a myriad of other purposes, it is a powerful tool. The
fact that it can be written as a `100 line macro
<macropy/tracing.py>`_ is a bonus.

Smart Asserts
~~~~~~~~~~~~~


.. code:: python

  from macropy.tracing import macros, require
  require[3**2 + 4**2 != 5**2]
  # Traceback (most recent call last):
  #   File "<console>", line 1, in <module>
  #   File "macropy.tracing.py", line 67, in handle
  #     raise AssertionError("Require Failed\n" + "\n".join(out))
  # AssertionError: Require Failed
  # 3**2 -> 9
  # 4**2 -> 16
  # 3**2 + 4**2 -> 25
  # 5**2 -> 25
  # 3**2 + 4**2 != 5**2 -> False


MacroPy provides a variant on the ``assert`` keyword called
``require``. Like ``assert``, ``require`` throws an ``AssertionError`` if the
condition is false.

Unlike ``assert``, ``require`` automatically tells you what code failed
the condition, and traces all the sub-expressions within the code so
you can more easily see what went wrong. Pretty handy!

``require`` can also be used in block form:

.. code:: python

  from macropy.tracing import macros, require
  with require:
      a > 5
      a * b == 20
      a < 2

  # Traceback (most recent call last):
  #   File "<console>", line 4, in <module>
  #   File "macropy.tracing.py", line 67, in handle
  #     raise AssertionError("Require Failed\n" + "\n".join(out))
  # AssertionError: Require Failed
  # a < 2 -> False


This requires every statement in the block to be a boolean
expression. Each expression will then be wrapped in a ``require()``,
throwing an ``AssertionError`` with a nice trace when a condition fails.

show_expanded
~~~~~~~~~~~~~

.. code:: python

  from ast import *
  from macropy.core.quotes import macros, q
  from macropy.tracing import macros, show_expanded

  print(show_expanded[q[1 + 2]])
  # BinOp(left=Num(n=1), op=Add(), right=Num(n=2))


``show_expanded`` is a macro which is similar to the simple ``log`` macro
shown above, but prints out what the wrapped code looks like *after
all macros have been expanded*. This makes it extremely useful for
debugging macros, where you need to figure out exactly what your code
is being expanded into. ``show_expanded`` also works in block form:

.. code:: python

  from macropy.core.quotes import macros, q
  from macropy.tracing import macros, show_expanded, trace

  with show_expanded:
      a = 1
      b = q[1 + 2]
      with q as code:
          print(a)

  # a = 1
  # b = BinOp(left=Num(n=1), op=Add(), right=Num(n=2))
  # code = [Print(dest=None, values=[Name(id='a', ctx=Load())], nl=True)]


These examples show how the `quasiquote`_ macro works:
it turns an expression or block of code into its AST, assigning the
AST to a variable at runtime for other code to use.

Here is a less trivial example: `case classes`_ are a
pretty useful macro, which saves us the hassle of writing a pile of
boilerplate ourselves. By using ``show_expanded``, we can see what the
case class definition expands into:

.. code:: python

  from macropy.case_classes import macros, case
  from macropy.tracing import macros, show_expanded

  with show_expanded:
      @case
      class Point(x, y):
          pass

  # class Point(CaseClass):
  #     def __init__(self, x, y):
  #         self.x = x
  #         self.y = y
  #         pass
  #     _fields = ['x', 'y']
  #     _varargs = None
  #     _kwargs = None
  #     __slots__ = ['x', 'y']


Pretty neat!

---------------------------------

If you want to write your own custom logging, tracing or debugging
macros, take a look at the `100 lines of code`__ that implements all
the functionality shown above.

__ macropy/tracing.py
