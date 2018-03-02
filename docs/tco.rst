.. _tco:

Tail-call Optimization
----------------------

.. code:: python

  from macropy.experimental.tco import macros, tco

  @tco
  def fact(n, acc=0):
      if n == 0:
          return acc
      else:
          return fact(n-1, n * acc)

  print(fact(10000))  # doesn't stack overflow
  # 28462596809170545189064132121198688901...


`Tail-call Optimization`__ is a technique which will optimize away the
stack usage of functions calls which are in a tail
position. Intuitively, if a function **A** calls another function
**B**, but does not do any computation after **B** returns (i.e. **A**
returns immediately when **B** returns), we don't need to keep around
the `stack frame <http://en.wikipedia.org/wiki/Call_stack>`_ for
**A**, which is normally used to store where to resume the computation
after **B** returns. By optimizing this, we can prevent really deep
tail-recursive functions (like the factorial example above) from
`overflowing the stack
<http://en.wikipedia.org/wiki/Stack_overflow>`_.

__ http://en.wikipedia.org/wiki/Tail_call


The ``@tco`` decorator macro doesn't just work with tail-recursive
functions, but also with any generic tail-calls (of either a function
or a method) via `trampolining`_, such this mutually
recursive example:

.. code:: python

  from macropy.experimental.tco import macros, tco

  class Example(object):

      @tco
      def odd(n):
      if n < 0:
          return odd(-n)
      elif n == 0:
          return False
      else:
          return even(n - 1)

      @tco
      def even(n):
          if n == 0:
              return True
          else:
              return odd(n-1)

  print(Example().even(100000))  # No stack overflow
  # True


Note that both ``odd`` and ``even`` were both decorated with ``@tco``.  All
functions which would ordinarily use too many stack frames must be
decorated.

Trampolining
~~~~~~~~~~~~

How is tail recursion implemented?  The idea is that if a function ``f``
would return the result of a recursive call to some function ``g``, it
could instead return ``g``, along with whatever arguments it would have
passed to ``g``.  Then instead of running ``f`` directly, we run
``trampoline(f)``, which will call ``f``, call the result of ``f``, call the
result of that ``f``, etc. until finally some call returns an actual
value.

A transformed (and simplified) version of the tail-call optimized
factorial would look like this

.. code:: python

  def trampoline_decorator(func):
      def trampolined(*args):
          if not in_trampoline():
              return trampoline(func, args)
          return func(*args)
      return trampolined

  def trampoline(func, args):
    _enter_trampoline()
    while True:
          result = func(*args)
          with patterns:
              if ('macropy-tco-call', func, args) << result:
                  pass
              else:
                  if ignoring:
                      _exit_trampoline()
                      return None
                  else:
                      _exit_trampoline()
                      return result

  @trampoline_decorator
  def fact(n, acc):
      if n == 0:
          return 1
      else:
          return ('macropy-tco-call', fact, [n-1, n * acc])
