# -*- coding: utf-8; mode: python -*-
"""
.. image:: https://travis-ci.org/azazel75/macropy.svg?branch=master
  :target: https://travis-ci.org/azazel75/macropy

.. warning::

   This is a customized version of the original `MacroPy`__
   updated to work only with Python 3.5+. PyPy is untested.

   As of now the original tests pass but some language features have
   yet to be implemented.

   What follows is an ongoing update of the original documentation and
   therefore may be inaccurate.

__ https://github.com/lihaoyi/macropy

MacroPy is an implementation of Macros in the Python Programming
Language.  MacroPy provides a mechanism for user-defined functions
(macros) to perform transformations on the abstract syntax tree(AST)
of Python code at module import time. This is an easy way to modify
the semantics of a python program

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

    print map(f[_[0]], ['omg', 'wtf', 'bbq'])
    # ['o', 'w', 'b']

    print reduce(f[_ + _], ['omg', 'wtf', 'bbq'])
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

And more! All this runs perfectly on vanilla Python 3.5+ (an maybe on
pypy, untested). For more details, see the `GitHub page
<https://github.com/azazel75/macropy#macropy>`_.  or ask in the
`Gitter channel <https://gitter.im/lihaoyi/macropy>`_ or the `Google
group <https://groups.google.com/forum/#!forum/macropy>`_ .

"""

from pathlib import Path
from setuptools import find_packages, setup
from macropy import __version__

here = Path(__file__).absolute().parent
with (here / 'CHANGES.rst').open(encoding='utf-8') as f:
    CHANGES = f.read()


setup(
    name='macropy3',
    version=__version__,
    description='Macros for Python: Quasiquotes, Case Classes, LINQ and more!',
    long_description=__doc__ + CHANGES,
    license='MIT',
    author='Li Haoyi, Justin Holmgren',
    author_email='haoyi.sg@gmail.com, justin.holmgren@gmail.com',
    maintainer='Alberto Berti',
    maintainer_email='alberto@metapensiero.it',
    url='https://github.com/azazel75/macropy',
    packages=find_packages(exclude=["*.test", "*.test.*"]),
    extras_require={
        'pyxl':  ["pyxl"],
        'pinq': ["SQLAlchemy"],
        'js_snippets': ["selenium", "pjs"],

    },
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
