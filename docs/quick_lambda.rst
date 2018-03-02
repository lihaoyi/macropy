.. _quicklambda:

Quick Lambdas
-------------

.. code:: python

  from macropy.quick_lambda import macros, f, _

  print(map(f[_ + 1], [1, 2, 3]))    # [2, 3, 4]
  print(reduce(f[_ * _], [1, 2, 3])) # 6


Macropy provides a syntax for lambda expressions similar to Scala's
`anonymous functions`__. Essentially, the transformation is:

__ http://www.codecommit.com/blog/scala/quick-explanation-of-scalas-syntax

.. code:: python

  f[_ * _] -> lambda a, b: a * b


where the underscores get replaced by identifiers, which are then set
to be the parameters of the enclosing ``lambda``.  This works too:

.. code:: python

  print(map(f[_.split(' ')[0]], ["i am cow", "hear me moo"]))
  # ['i', 'hear']


Quick Lambdas can be also used as a concise, lightweight,
more-readable substitute for ``functools.partial``

.. code:: python

  from macropy.quick_lambda import macros, f
  basetwo = f[int(_, base=2)]
  print(basetwo('10010')) # 18


is equivalent to

.. code:: python

  import functools
  basetwo = functools.partial(int, base=2)
  print(basetwo('10010')) # 18


Quick Lambdas can also be used entirely without the `_` placeholders,
in which case they wrap the target in a no argument ``lambda: ...``
thunk:

.. code:: python

  from random import random
  thunk = f[random() * 2 + 3]
  print(thunk()) # 4.522011062548173
  print(thunk()) # 4.894243231792029


This cuts out reduces the number of characters needed to make a thunk
from 7 (using ``lambda``) to 2, making it much easier to use thunks to
do things like emulating `by name parameters`__. The implementation of
quicklambda is about :repo:`30 lines of code
<macropy/quick_lambda.py>`, and is worth a look if you want to see how
a simple (but extremely useful!) macro can be written.

__ http://locrianmode.blogspot.com/2011/07/scala-by-name-parameter.html
