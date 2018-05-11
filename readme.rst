.. -*- coding: utf-8 -*-

=============================
 MacroPy3 1.1.0b2
=============================

.. image:: https://travis-ci.org/azazel75/macropy.svg?branch=master
  :target: https://travis-ci.org/azazel75/macropy

**MacroPy** is an implementation of `Syntactic Macros
<http://tinyurl.com/cmlls8v>`_ in the `Python Programming Language
<http://python.org/>`_. MacroPy provides a mechanism for user-defined
functions (macros) to perform transformations on the `abstract syntax
tree <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`_ (AST) of a
Python program at *import time*. This is an easy way to enhance the
semantics of a Python program in ways which are otherwise impossible,
for example providing an extremely concise way of declaring classes.

Python like you've never seen before
====================================

MacroPy allows you to create constructs which are impossible to have
in normal python code, such as:

Tracing
-------

.. code:: python

    with trace:
        sum([x + 5 for x in range(3)])

    # sum([x + 5 for x in range(3)])
    # range(3) -> [0, 1, 2]
    # x + 5 -> 5
    # x + 5 -> 6
    # x + 5 -> 7
    # [x + 5 for x in range(3)] -> [5, 6, 7]
    # sum([x + 5 for x in range(3)]) -> 18

Quick Lambdas
-------------

.. code:: python

    print(list(map(f[_[0]], ['omg', 'wtf', 'bbq'])))
    # ['o', 'w', 'b']

    print(list(reduce(f[_ + _], ['omg', 'wtf', 'bbq'])))
    # 'omgwtfbbq

Case Classes
------------

.. code:: python

    @case
    class Point(x, y): pass

    p = Point(1, 2)

    print str(p)    #Point(1, 2)
    print p.x       #1
    print p.y       #2
    print Point(1, 2) == Point(1, 2) # True

and more! See the docs at
`<http://macropy3.readthedocs.io/en/latest/>`_.

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

How to contribute
=================

We're open to contributions, so send us your
ideas/questions/issues/pull-requests and we'll do our best to
accommodate you! You can ask questions on the `Google Group
<https://groups.google.com/forum/#!forum/macropy>`_  and on the
`Gitter channel <https://gitter.im/lihaoyi/macropy>`_ or file bugs on
thee `issues`__ page.

__ https://github.com/lihaoyi/macropy/issues

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

Copyright (c) 2013-2018, `Li Haoyi <https://github.com/lihaoyi>`_, `Justin
Holmgren <https://github.com/jnhnum1>`_, `Alberto Berti
<https://github.com/azazel75>`_ and all the other contributors

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
