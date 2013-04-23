MacroPy
=======

**MacroPy** is an implementation of [Macros](http://tinyurl.com/cmlls8v) in the [Python Programming Language](http://python.org/). MacroPy provides a mechanism for user-defined functions (*macros*) to perform transformations on the [abstract syntax tree](http://en.wikipedia.org/wiki/Abstract_syntax_tree) of Python code at _module import time_. This is an easy way to modify the semantics of a python program, and has been used to implement features such as:

- [Quasiquotes](), a quick way to manipulate fragments of a program
- [String Interpolation](), a common feature in many languages
- [Tracing]() and [Smart Asserts]()
- [Pattern Matching]() from the Functional Programming world
- [LINQ to SQL]() from C#
- [Lightweight Anonymous Functions]() from Scala and Groovy

All of these are advanced language features that each would have been a massive effort to implement in the [CPython](http://en.wikipedia.org/wiki/CPython) interpreter. Using macros, the implementation of each feature fits in a single file, often taking less than 40 lines of code.

Quasiquotes
-----------

```python
a = 10
b = 2
tree = q%(1 + u%(a + b))
print tree
#BinOp(Num(1), Add(), Num(12))
```

String Interpolation
--------------------

```python
a, b = 1, 2
c = s%"%{a} apple and %{b} bananas"
print c
#1 apple and 2 bananas
```

Tracing
-------

Smart Asserts
-------------

Pattern Matching
----------------

LINQ to SQL
-----------

Lightweight Anonymous Functions
-------------------------------
