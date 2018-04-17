.. _interned:

Interned
--------

.. code:: python

  from macropy.quick_lambda import macros, interned

  # count how many times expensive_func runs
  count = [0]
  def expensive_func():
      count[0] += 1

  def func():
      return interned[expensive_func()]

  print(count[0] # 0)
  func()
  print(count[0] # 1)
  func()
  print(count[0] # 1)

The ``interned`` macro is similar to the :ref:`Lazy <lazy>` macro in
that the code within the ``interned[...]`` block is wrapped in a thunk
and evaluated at most once. Unlike the ``lazy`` macro, however,
``interned`` does not created a memoizing thunk that you can pass
around your program; instead, the memoization is done on a
*per-use-site* basis.

As you can see in the example above, although ``func`` is called
repeatedly, the ``expensive_func()`` call within the ``interned``
block is only ever evaluated once. This is handy in that it gives you
a mechanism for memoizing a particular computation without worrying
about finding a place to store the memoized values. It's just memoized
globally (often what you want) while being scoped locally, which
avoids polluting the global namespace with names only relevant to a
single function (also often what you want).
