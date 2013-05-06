"""
MacroPy
-------

**MacroPy** is an implementation of Macros in the Python Programming Language. MacroPy provides a mechanism for user-defined functions (macros) to perform transformations on the [abstract syntax tree](http://en.wikipedia.org/wiki/Abstract_syntax_tree)(AST) of Python code at module import time. This is an easy way to modify the semantics of a python program.

.. code:: python
    from macropy.macros.quicklambda import macros, f
    from macropy.macros.adt import macros, case

    prit reduce(f%(_ + _), [1, 2, 3])   # 6

    @case
    class Point(x, y): pass

    p = Point(1, 2)
    print p.x                           # 1
See the [GitHub page](https://github.com/lihaoyi/macropy) for full documentation.
"""
from distutils.core import setup

setup(name='MacroPy',
      version='0.1.1',
      description='Macros for Python: Quasiquotes, Case Classes, LINQ and more!'
                'and good intentions',
      long_description=__doc__,
      author='Li Haoyi',
      author_email='haoyi.sg@gmail.com',
      url='https://github.com/lihaoyi/macropy',
      packages=['macropy', 'macropy.core', 'macropy.macros', 'macropy.macros2'],
     )