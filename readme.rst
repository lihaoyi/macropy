.. -*- coding: utf-8 -*-

================
 MacroPy 1.0.4
================

.. image:: https://travis-ci.org/azazel75/macropy.svg?branch=master
  :target: https://travis-ci.org/azazel75/macropy

.. warning::

   This is a fork of the original `MacroPy`__ updated to work only
   with Python 3.4+. PyPy and Jython are untested.

   All the test have been updated to cover mothern Python 3.4+ syntax.

   This package is published as ``macropy3`` on `pypi`__.

   What follows is an ongoing update of the original documentation and
   therefore may be inaccurate.

__ https://github.com/lihaoyi/macropy
__ https://pypi.python.org/pypi/macropy3

**MacroPy** is an implementation of `Syntactic Macros
<http://tinyurl.com/cmlls8v>`_ in the `Python Programming Language
<http://python.org/>`_. MacroPy provides a mechanism for user-defined
functions (macros) to perform transformations on the `abstract syntax
tree <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`_ (AST) of a
Python program at *import time*. This is an easy way to enhance the
semantics of a Python program in ways which are otherwise impossible,
for example providing an extremely concise way of declaring classes:

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
`docs/examples/using_macros <docs/examples/using_macros>`_ folder for
a minimal example of using MacroPy's existing macros.

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


Browse the `high-level overview`_, or look at the `Tutorials`_ will go
into greater detail and walk you through

.. _high-level overview: `30,000ft Overview`_

- `Writing your first macro`_
- `Making your macros hygienic`_
- `Exporting your Expanded Code`_

The `Reference`_ documentation contains information about:

- `Data Model`_, what MacroPy gives you to work with;
- `Arguments`_, what a macro is given to do its work;
- `Quasiquotes`_, a quick way to manipulate AST fragments;
- `Walkers`_, a flexible tool to traverse and transform ASTs;
- `Hygiene`_, how to avoid weird bugs related to name
  collisions and shadowing;
- `Expansion Failures`_, what happens when a
  macro doesn't work;
- `Expansion Order`_ of nested macros with a file;
- `Line Numbers`_, or what errors you get when
  something goes wrong;


Or just skip ahead to the `Discussion`_ and `Conclusion
<#macropy-bringing-macros-to-python>`_. We're open to contributions,
so send us your ideas/questions/issues/pull-requests and we'll do our
best to accommodate you! You can ask questions on the `Google Group
<https://groups.google.com/forum/#!forum/macropy>`_ or file bugs on
thee `issues <issues>`_ page. See the `changelist <changes.md>`_ to
see what's changed recently.

MacroPy is tested to run on `CPython 2.7.2
<http://en.wikipedia.org/wiki/CPython>`_ and `PyPy 2.0
<http://pypy.org/>`_, but with only partial support for Python 3.X
(You'll need to clone the `python3 branch
<https://github.com/lihaoyi/macropy/tree/python3>`_ yourself) and no
support for `Jython <http://www.jython.org/>`_. MacroPy is also
available on `PyPI <https://pypi.python.org/pypi/MacroPy>`_, using a
standard `setup.py <setup.py>`_ to manage dependencies, installation
and other things. Check out `this gist
<https://gist.github.com/lihaoyi/5577609>`_ for an example of setting
it up on a clean system.


MacroPy: Bringing Macros to Python
==================================

Macros are always a contentious issue. On one hand, we have the
`Lisp`_ community, which seems to using macros for everything. On the
other hand, most mainstream programmers shy away from them, believing
them to be extremely powerful and potentially confusing, not to
mention extremely difficult to execute.

With MacroPy, we believe that we have a powerful, flexible tool that
makes it trivially easy to write AST-transforming macros with any
level of complexity. We have a `compelling suite of use cases
<#examples>`_ demonstrating the utility of such transforms, and all of
it runs perfectly fine on alternative implementations of Python such
as PyPy.

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

The MIT License (MIT)

Copyright (c) 2013, `Li Haoyi <https://github.com/lihaoyi>`_, `Justin
Holmgren <https://github.com/jnhnum1>`_

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
