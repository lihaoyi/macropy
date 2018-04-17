.. MacroPy3 documentation master file, created by
   sphinx-quickstart on Wed Feb 28 23:22:39 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MacroPy3's documentation!
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   tutorials
   demo
   experimental
   discussion
   reference


MacroPy3 is a port of the original MacroPy to Python 3. If you look for
the Python 2 version see the `python2 branch`__

__ https://github.com/lihaoyi/macropy/tree/python2

**MacroPy** is an implementation of `Syntactic Macros`__ in the
`Python Programming Language <http://python.org/>`_. MacroPy provides
a mechanism for user-defined functions (macros) to perform
transformations on the `abstract syntax tree`__ (AST) of a
Python program at *import time*. This is an easy way to enhance the
semantics of a Python program in ways which are otherwise impossible,
for example providing an extremely concise way of declaring classes:

__ //en.wikipedia.org/wiki/Macro_(computer_science)#Syntactic_macros
__ //en.wikipedia.org/wiki/Abstract_syntax_tree

.. code:: python

  >>> import macropy.console
  0=[]=====> MacroPy Enabled <=====[]=0
  >>> from macropy.case_classes import macros, case

  >>> @case
  class Point(x, y): pass

  >>> p = Point(1, 2)
  >>> print(p.x)
  1
  >>> print(p)
  Point(1, 2)


Try it out in the REPL, it should just work! You can also see the
:repo:`docs/examples/using_macros` folder for a minimal example of using
MacroPy's existing macros.

MacroPy has been used to implement features such as:

- `case_classes`:ref:, easy Algebraic Data Types from Scala, and `enums`:ref:;
- `quicklambda`:ref: from Scala and Groovy, and the `lazy`:ref: and
  `interned`:ref: utility macros;
- `interpolation`:ref:, a common feature in many programming
    languages;
- `tracing`:ref: and `asserts`:ref:, and `show_expanded`:ref:, to help
  in the debugging effort;
- `peg`:ref:, Parser Combinators inspired by Scala's,


As well as a number of more experimental macros such as:

- `pattern`:ref: from the Functional Programming world
- `tco`:ref:, preventing unnecessary stack overflows
- `pinq`:ref:, a shameless clone of LINQ to SQL from C#
- `pyxl_snippets`:ref:, XML interpolation within your Python code
- `js`:ref:, cross compiling snippets of Python into equivalent
  Javascript


Browse the :ref:`high-level overview <overview>`, or look at the
`Tutorials`:ref: will go into greater detail and walk you through

- `first_macro`:ref:
- `hygienic_macro`:ref:
- `exporting`:ref:

Or just skip ahead to the `discussion`:ref: and
`conclusion`:ref:. We're open to contributions, so send us your
ideas/questions/issues/pull-requests and we'll do our best to
accommodate you! You can ask questions on the `Google Group
<https://groups.google.com/forum/#!forum/macropy>`_  and on the
`Gitter channel <https://gitter.im/lihaoyi/macropy>`_ or file bugs on
thee `issues`__ page. See the `changelist <CHANGES.rst>`:repo: to
see what's changed recently.

__ https://github.com/lihaoyi/macropy/issues

Requirements
============

MacroPy3 is tested to run on `CPython 3.4
<http://en.wikipedia.org/wiki/CPython>`_ or newer and `PyPy
<http://pypy.org/>`_ 3.5. I has no current support for `Jython
<http://www.jython.org/>`_. MacroPy3 is also available on `PyPI
<https://pypi.python.org/pypi/macropy3>`_.

Installation
============

Just execute a:

.. code:: console

   $ pip install macropy3

if you want to use macros that require external libraries in order to
work, you can automatically install those dependencies by installing
one of the ``pinq`` or ``pyxl`` extras like this:

.. code:: console

   $ pip install macropy3[pinq,pyxl]


then have a look at the docs at `<http://macropy3.readthedocs.io/en/latest/>`_.

.. _conclusion:

MacroPy: Bringing Macros to Python
==================================

Macros are always a contentious issue. On one hand, we have the
LISP community, which seems to using macros for everything. On the
other hand, most mainstream programmers shy away from them, believing
them to be extremely powerful and potentially confusing, not to
mention extremely difficult to execute.

With MacroPy, we believe that we have a powerful, flexible tool that
makes it trivially easy to write AST-transforming macros with any
level of complexity. We have a `compelling suite of use cases
<demo>`_ demonstrating the utility of such transforms.

.. and all of it runs perfectly fine on alternative implementations of
.. Python such as PyPy.

Credits
=======

MacroPy was initially created as a final project for the `MIT
<http://web.mit.edu/>`_ class `6.945: Adventures in Advanced Symbolic
Programming <http://groups.csail.mit.edu/mac/users/gjs/6.945/>`_,
taught by `Gerald Jay Sussman
<http://groups.csail.mit.edu/mac/users/gjs/>`_ and `Pavel Panchekha
<http://pavpanchekha.com/>`_. Inspiration was taken from project such
as `Scala Macros <http://scalamacros.org/>`_, `Karnickel
<https://pypi.python.org/pypi/karnickel>`_ and `Pyxl
<https://github.com/dropbox/pyxl>`_.

License
=======

MIT

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
