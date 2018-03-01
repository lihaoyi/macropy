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
   reference


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

  >>> import macropy.consol)e
  0=[]=====> MacroPy Enabled <=====[]=0
  >>> from macropy.case_classes import macros, case

  >>> @case
  class Point(x, y): pass

  >>> p = Point(1, 2)
  >>> print p.x
  1
  >>> print p
  Point(1, 2)


Try it out in the REPL, it should just work! You can also see the
`docs/examples/using_macros`__ folder for a minimal example of using
MacroPy's existing macros.

__ //github.com/azazel75/macropy/tree/master/docs/examples/using_macros


MacroPy has been used to implement features such as:

- `Case Classes`_, easy Algebraic Data Types from Scala, and `Enums`_;
- `Quick Lambdas`_ from Scala and Groovy, and the `Lazy`_ and
  `Interned`_ utility macros;
- `String Interpolation`_, a common feature in many programming
  languages;
- `Tracing`_ and `Smart Asserts`_, and `show_expanded`_, to help in
  the debugging effort;
- `MacroPEG`_, Parser Combinators inspired by Scala's,


As well as a number of more experimental macros such as:

- `Pattern Matching`_ from the Functional Programming world
- `Tail-call Optimization`_, preventing unnecessary stack overflows
- `PINQ to SQLAlchemy`_, a shameless clone of LINQ to SQL from C#
- `Pyxl Snippets`_, XML interpolation within your Python code
- `JS Snippets`_, cross compiling snippets of Python into equivalent
  Javascript


Browse the :ref:`high-level overview <overview>`, or look at the
`Tutorials`_ will go into greater detail and walk you through

- `Writing your first macro`_
- `Making your macros hygienic`_
- `Exporting your Expanded Code`_


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
