.. _lazy:

Lazy
----

.. code:: python

  from macropy.quick_lambda import macros, lazy

  # count how many times expensive_func runs
  count = [0]
  def expensive_func():
      count[0] += 1

  thunk = lazy[expensive_func()]

  print count[0] # 0

  thunk()
  print(count[0]) # 1
  thunk()
  print(count[0]) # 1

The ``lazy`` macro is used to create a memoizing thunk. Wrapping an
expression with ``lazy`` creates a thunk which needs to be applied
(e.g. ``thunk()``) in order to get the value of the expression
out. This macro then memoizes the result of that expression, such that
subsequent calls to ``thunk()`` will not cause re-computation.

This macro is a tradeoff between declaring the value as a variable:

.. code:: python

  var = expensive_func()


Which evaluates exactly once, even when not used, and declaring it as
a function:

.. code:: python

  thunk = lambda: expensive_func()


Which no longer evaluates when not used, but now re-evaluates every
single time. With ``lazy``, you get an expression that evaluates 0 or 1
times. This way, you don't have to pay the cost of computation if it
is not used at all (the problems with variables) or the cost of
needlessly evaluating it more than once (the problem with lambdas).

This is handy to have if you know how to compute an expression in a
local scope that may be used repeatedly later. It may depend on many
local variables, for example, which would be inconvenient to pass
along to the point at which you know whether the computation is
necessary. This way, you can simply "compute" the lazy value and pass
it along, just as you would compute the value normally, but with the
benefit of only-if-necessary evaluation.
