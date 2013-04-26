MacroPy
=======

**MacroPy** is an implementation of [Macros](http://tinyurl.com/cmlls8v) in the [Python Programming Language](http://python.org/). MacroPy provides a mechanism for user-defined functions (macros) to perform transformations on the [abstract syntax tree](http://en.wikipedia.org/wiki/Abstract_syntax_tree)(AST) of Python code at _module import time_. This is an easy way to modify the semantics of a python program, and has been used to implement features such as:

- [Quasiquotes](#quasiquotes), a quick way to manipulate fragments of a program
- [String Interpolation](#string-interpolation), a common feature in many languages
- [Tracing](#tracing) and [Smart Asserts](#smart-asserts)
- [Case Classes](Case-Classes), easy [Algebraic Data Types](https://en.wikipedia.org/wiki/Algebraic_data_type) from Scala
- [Pattern Matching](#pattern-matching) from the Functional Programming world
- [LINQ to SQL](#linq-to-sql) from C#
- [Quick Lambdas](#quick-lambdas) from Scala and Groovy,

All of these are advanced language features that each would have been a massive effort to implement in the [CPython](http://en.wikipedia.org/wiki/CPython) interpreter. Using macros, the implementation of each feature fits in a single file, often taking less than 40 lines of code.

*MacroPy is very much a work in progress, for the [MIT](http://web.mit.edu/) class [6.945: Adventures in Advanced Symbolic Programming](http://groups.csail.mit.edu/mac/users/gjs/6.945/). Although it is constantly in flux, all of the examples with source code represent already-working functionality. The rest will be filled in over the coming weeks.*

Rough Overview
--------------
Macro functions are defined in two ways:

```python
@expr_macro
def my_expr_macro(tree):
    ...
    return new_tree

@block_macro
def my_block_macro(tree):
    ...
    return new_tree
```

These two types of macros are called via

```python
val = my_expr_macro%(...)

with my_block_macro:
    ...
```

Any time either of these syntactic forms is seen, if a matching macro exists, the abstract syntax tree captured by these forms (the `...` in the code above) is given to the respective macro to handle. The macro can then return a new tree, which is substituted into the original code in-place.

MacroPy intercepts the module-loading workflow, via the functionality provided by [PEP 302: New Import Hooks](http://www.python.org/dev/peps/pep-0302/). The workflow is roughly:

- Intercept an import
- Parse the contents of the file into an AST
- walk the AST and expand any macros that it finds
- unparse the AST back into a string and resume loading it as a module

Below are a few example uses of macros that are implemented (together with test cases!) in the [macropy/macros](macropy/macros) folder.

Quasiquotes
-----------

```python
a = 10
b = 2
tree = q%(1 + u%(a + b))
print tree
#BinOp(Num(1), Add(), Num(12))
```

Quasiquotes are the foundation for many macro systems, such as that found in [LISP](http://en.wikipedia.org/wiki/LISP). Quasiquotes save you from having to manually construct code trees from the nodes they are made of. For example, if you want the code tree for 

```python
(1 + 2)
```

Without quasiquotes, you would have to build it up by hand:

```python
tree = BinOp(Num(1), Add(), Num(2))
```

But with quasiquotes, you can simply write the code `(1 + 2)`, quoting it with `q%` to lift it from an expression (to be evaluated) to a tree (to be returned):

```python
tree = q%(1 + 2)
```

Furthermore, quasiquotes allow you to _unquote_ things: if you wish to insert the **value** of an expression into the tree, rather than the **tree** making up the expression, you unquote it using `u%`. In the example above:

```python
tree = q%(1 + u%(a + b))
```

the expression `(a + b)` is unquoted. Hence `a + b` gets evaluated to the value of `12`, which is then inserted into the tree, giving the final tree:

```python
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

Unlike the normal string interpolation in Python, MacroPy's string interpolation allows the programmer to specify the variables to be interpolated _inline_ inside the string. The macro `s%` then takes the string literal

```python
"%{a} apple and %{b} bananas"
```

and expands it into the expression

```python
"%s apple and %s bananas" % (a, b)
```

Which is evaluated at run-time in the local scope, using whatever the values `a` and `b` happen to hold at the time. The contents of the `%{...}` can be any arbitrary python expression, and is not limited to variable names.

Tracing
-------

```python
log%(1 + 2)
#(1 + 2) -> 3

log%("omg" * 3)
#('omg' * 3) -> 'omgomgomg'
```

Tracing allows you to easily see what is happening inside your code. Many a time programmers have written code like

```python
print "value", value
print "sqrt(x)", sqrt(x)
```

and the `log%` macro (shown above) helps remove this duplication by automatically expanding `log%(1 + 2)` into `wrap("(1 + 2)", (1 + 2))`. `wrap` then evaluates the expression, printing out the source code and final value of the computation.

In addition to simple logging, MacroPy provides the `trace%` macro. This macro not only logs the source and result of the given expression, but also the source and result of all sub-expressions nested within it:

```python
trace%[len(x)*3 for x in ["omg", "wtf", "b" * 2 + "q", "lo" * 3 + "l"]]
#('b' * 2) -> 'bb'
#(('b' * 2) + 'q') -> 'bbq'
#('lo' * 3) -> 'lololo'
#(('lo' * 3) + 'l') -> 'lololol'
#['omg', 'wtf', (('b' * 2) + 'q'), (('lo' * 3) + 'l')] -> ['omg', 'wtf', 'bbq', 'lololol']
#len(x) -> 3
#(len(x) * 3) -> 9
#len(x) -> 3
#(len(x) * 3) -> 9
#len(x) -> 3
#(len(x) * 3) -> 9
#len(x) -> 7
#(len(x) * 3) -> 21
#[(len(x) * 3) for x in ['omg', 'wtf', (('b' * 2) + 'q'), (('lo' * 3) + 'l')]] -> [9, 9, 9, 21]
```

As you can see, `trace%` logs the source and value of all sub-expressions that get evaluated in the course of evaluating the list comprehension.

Lastly, `trace` can be used as a block macro:


```python
with trace:
    sum = 0
    for i in range(0, 5):
        sum = sum + 5

    square = sum * sum
#sum = 0
#for i in range(0, 5):
#   sum = (sum + 5)
#range(0, 5) -> [0, 1, 2, 3, 4]
#sum = (sum + 5)
#(sum + 5) -> 5
#sum = (sum + 5)
#(sum + 5) -> 10
#sum = (sum + 5)
#(sum + 5) -> 15
#sum = (sum + 5)
#(sum + 5) -> 20
#sum = (sum + 5)
#(sum + 5) -> 25
#square = (sum * sum)
#(sum * sum) -> 625
```

Used this way, `trace` will print out the source code of every _statement_ that gets executed, in addition to tracing the evaluation of any expressions within those statements.

Smart Asserts
-------------
```python
require%(3**2 + 4**2 != 5**2)
#AssertionError: Require Failed
#(3 ** 2) -> 9
#(4 ** 2) -> 16
#((3 ** 2) + (4 ** 2)) -> 25
#(5 ** 2) -> 25
#(((3 ** 2) + (4 ** 2)) != (5 ** 2)) -> False
```

MacroPy provides a variant on the `assert` keyword called `require%`. Like `assert`, `require%` throws an `AssertionError` if the condition is false.

Unlike `assert`, `require%` automatically tells you what code failed the condition, and traces all the sub-expressions within the code so you can more easily see what went wrong. Pretty handy!

`require% can also be used in block form:

```python
a = 10
b = 2
with require:
    a > 5
    a * b == 20
    a < 2
#AssertionError: Require Failed
#(a < 2) -> False
```

This requires every statement in the block to be a boolean expression. Each expression will then be wrapped in a `require%`, throwing an `AssertionError` with a nice trace when a condition fails.

Case Classes
------------
```python
@case
class Point(x, y): pass

p = Point(1, 2)

print str(p)
#Point(1, 2)

print p.x
#1

print p.y
#2

print Point(1, 2) == Point(1, 2)
```

[Case classes](http://www.codecommit.com/blog/scala/case-classes-are-cool) are classes with extra goodies:

- A nice `__str__` method is autogenerated
- An autogenerated constructor
- Structural equality by default

The reasoning being that although you may sometimes want complex, custom-built classes with custom features and fancy inheritance, very (very!) often you want a simple class with a constructor, pretty `__str__` and `__repr__` methods, and structural equality which doesn't inherit from anything. Case classes provide you just that, with an extremely concise declaration.

Pattern Matching
----------------
*Work-In-Progress*

LINQ to SQL
-----------
```python
print sql%(
    x.name for x in bbc
    if x.gdp / x.population > (
        y.gdp / y.population for y in bbc
        if y.name == 'United Kingdom'
    ) and x.region == 'Europe'
)
#SELECT name FROM bbc
#WHERE gdp/population > (
#    SELECT gdp/population FROM bbc
#    WHERE name = 'United Kingdom'
#)
#AND region = 'Europe'
```

This feature is inspired by [C#'s LINQ to SQL](http://msdn.microsoft.com/en-us/library/bb386976.aspx). In short, code used to manipulate lists is lifted into an AST which is then cross-compiled into a snippet of [SQL](http://en.wikipedia.org/wiki/SQL).

This allows you to write queries to a database in the same way you would write queries on in-memory lists. *WIP*

Quick Lambdas
-------------------------------
```python
map(f%(_ + 1), [1, 2, 3])
#[2, 3, 4]

reduce(f%(_ + _), [1, 2, 3])
#6
```

Macropy provides a syntax for lambda expressions similar to Scala's [anonymous functions](http://www.codecommit.com/blog/scala/quick-explanation-of-scalas-syntax). Essentially, the transformation is:

```python
f%(_ + _) -> lambda a, b: a + b
```

where the underscores get replaced by identifiers, which are then set to be the parameters of the enclosing `lambda`. This works too:

```python
map(f%_.split(' ')[0], ["i am cow", "hear me moo"])
#["i", "hear"]
```

Quick Lambdas can be also used as a concise, lightweight, more-readable substitute for `functools.partial`

```python
import functools
basetwo = functools.partial(int, base=2)
basetwo('10010')
#18
```

is equivalent to

```python
basetwo = f%int(_, base=2)
basetwo('10010')
#18
```

Quick Lambdas can also be used entirely without the `_` placeholders, in which case they wrap the target in a no argument `lambda: ...` thunk:

```python
from random import random
thunk = f%random()
print thunk()
#0.5497242707566372
print thunk()
#0.3068253802774531
```

This cuts out reduces the number of characters needed to make a thunk from 7 to 2, making it much easier to use thunks to do things like emulating [by name parameters](http://locrianmode.blogspot.com/2011/07/scala-by-name-parameter.html).

