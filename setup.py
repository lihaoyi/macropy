"""

MacroPy is an implementation of Macros in the Python Programming Language.
MacroPy provides a mechanism for user-defined functions (macros) to perform
transformations on the abstract syntax tree(AST) of Python code at module
import time. This is an easy way to modify the semantics of a python program

Python like you've never seen before
------------------------------------

MacroPy allows you to create constructs which are impossible to have in normal
python code, such as:

Tracing
```````
.. code:: python

    with trace:
        sum([x + 5 for x in range(3)])

    # sum([(x + 5) for x in range(3)])
    # range(3) -> [0, 1, 2]
    # (x + 5) -> 5
    # (x + 5) -> 6
    # (x + 5) -> 7
    # [(x + 5) for x in range(3)] -> [5, 6, 7]
    # sum([(x + 5) for x in range(3)]) -> 18

Quick Lambdas
`````````````

.. code:: python

    print map(f%_[0], ['omg', 'wtf', 'bbq'])
    # ['o', 'w', 'b']

    print reduce(f%(_ + _), ['omg', 'wtf', 'bbq'])
    # 'omgwtfbbq

Case Classes
````````````

.. code:: python

    @case
    class Point(x, y): pass

    p = Point(1, 2)

    print str(p)    #Point(1, 2)
    print p.x       #1
    print p.y       #2
    print Point(1, 2) == Point(1, 2) # True

And more! All this runs perfectly on vanilla Python 2.7 or PyPy 2.0. For more details, see the `GitHub page <https://github.com/lihaoyi/macropy>`_
"""


from setuptools import find_packages, setup
from macropy import __version__

setup(
    name='MacroPy',
    version=__version__,
    description='Macros for Python: Quasiquotes, Case Classes, LINQ and more!',
    long_description=__doc__,
    license='BSD',
    author='Li Haoyi, Justin Holmgren',
    author_email='haoyi.sg@gmail.com, justin.holmgren@gmail.com',
    url='https://github.com/lihaoyi/macropy',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    extras_require = {
        'pyxl':  ["pyxl"],
        'pinq': ["SQLAlchemy"],
        'js_snippets': ["selenium", "pjs"],
    },
    classifiers=['Programming Language :: Python :: 2.7']
)
