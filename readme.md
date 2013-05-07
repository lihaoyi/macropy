MacroPy
=======

**MacroPy** is an implementation of [Macros](http://tinyurl.com/cmlls8v) in the [Python Programming Language](http://python.org/). MacroPy provides a mechanism for user-defined functions (macros) to perform transformations on the [abstract syntax tree](http://en.wikipedia.org/wiki/Abstract_syntax_tree)(AST) of Python code at _module import time_. This is an easy way to modify the semantics of a python program, and has been used to implement features such as:

- [Quasiquotes](#quasiquotes), a quick way to manipulate fragments of a program
- [String Interpolation](#string-interpolation), a common feature in many languages
- [Pyxl](#pyxl-integration), integrating XML markup into a Python program
- [Tracing](#tracing) and [Smart Asserts](#smart-asserts)
- [Case Classes](#case-classes), easy [Algebraic Data Types](https://en.wikipedia.org/wiki/Algebraic_data_type) from Scala
- [Pattern Matching](#pattern-matching) from the Functional Programming world
- [Tail-call Optimization](#tco)
- [LINQ to SQL](#linq-to-sql) from C#
- [Quick Lambdas](#quick-lambdas) from Scala and Groovy,
- [Parser Combinators](#parser-combinators), inspired by [Scala's](http://www.suryasuravarapu.com/2011/04/scala-parser-combinators-win.html).

MacroPy is tested to run on:

- [CPython 2.7.2](http://en.wikipedia.org/wiki/CPython)
- [PyPy 1.9](http://pypy.org/)

It does not yet work on [Jython](http://www.jython.org/), and is available on [PyPI](https://pypi.python.org/pypi/MacroPy).

All of these are advanced language features that each would have been a massive effort to implement in the [CPython](http://en.wikipedia.org/wiki/CPython) interpreter. Using macros, the implementation of each feature fits in a single file, often taking less than 40 lines of code.

*MacroPy is very much a work in progress, for the [MIT](http://web.mit.edu/) class [6.945: Adventures in Advanced Symbolic Programming](http://groups.csail.mit.edu/mac/users/gjs/6.945/). Although it is constantly in flux, all of the examples with source code represent already-working functionality. The rest will be filled in over the coming weeks.*

Rough Overview
--------------
Macro functions are defined in three ways:

```python
macros = Macros()
@macros.expr
def my_expr_macro(tree):
    ...
    return new_tree

@macros.block
def my_block_macro(tree):
    ...
    return new_tree

@macros.decorator
def my_decorator_macro(tree):
    ...
    return new_tree
```

These three types of macros are called via

```python
val = my_expr_macro%(...)

with my_block_macro:
    ...

@my_decorator_macro
class X():
    ...
```

Any time any of these syntactic forms is seen, if a matching macro exists, the abstract syntax tree captured by these forms (the `...` in the code above) is given to the respective macro to handle. The macro can then return a new tree, which is substituted into the original code in-place.

MacroPy intercepts the module-loading workflow, via the functionality provided by [PEP 302: New Import Hooks](http://www.python.org/dev/peps/pep-0302/). The workflow is roughly:

- Intercept an import
- Parse the contents of the file into an AST
- Walk the AST and expand any macros that it finds
- Compile the modified AST and resume loading it as a module

![Workflow](media/Workflow.png)

Below are a few example uses of macros that are implemented (together with test cases!) in the [macropy/macros](macropy/macros) folder.

Quasiquotes
-----------

```python
a = 10
b = 2
tree = q%(1 + u%(a + b))
print ast.dump(tree)
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
print ast.dump(tree)
#BinOp(Num(1), Add(), Num(12))
```

the expression `(a + b)` is unquoted. Hence `a + b` gets evaluated to the value of `12`, which is then inserted into the tree, giving the final tree.

Apart from interpolating values in the AST, you can also interpolate:

###Other ASTs

```python
a = q%(1 + 2)
b = q%(ast%a + 3)
print ast.dump(b)
#BinOp(BinOp(Num(1), Add(), Num(2)), Add(), Num(3))
```

This is necessary to join together ASTs directly, without converting the interpolated AST into its `repr`. If we had used the `u%` interpolator, it fails with an error

###Names
```python
n = "x"
x = 1
y = q%(name%n + name%n)
print ast.dump(y)
#BinOp(Name('x'), Add(), Name('x'))
```

This is convenient in order to interpolate a string variable as an identifier, rather than interpolating it as a string literal.


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

Pyxl Integration
----------------

```python
image_name = "bolton.png"
image = p%'<img src="/static/images/{image_name}" />'

text = "Michael Bolton"
block = p%'<div>{image}{text}</div>'

element_list = [image, text]
block2 = p%'<div>{element_list}</div>'

assert block2.to_string() == '<div><img src="/static/images/bolton.png" />Michael Bolton</div>'
```

[Pyxl](https://github.com/dropbox/pyxl) is a way of integrating XML markup into your Python code. By default, pyxl hooks into the python UTF-8 decoder in order to transform the source files at load-time. In this, it is similar to how MacroPy transforms source files at import time.

A major difference is that Pyxl by default leaves the HTML fragments directly in the source code:

```python
image_name = "bolton.png"
image = <img src="/static/images/{image_name}" />

text = "Michael Bolton"
block = <div>{image}{text}</div>

element_list = [image, text]
block2 = <div>{element_list}</div>
```

While the MacroPy version requires each snippet to be wrapped in a `p%"..."` wrapper. This [three-line-of-code macro](https://github.com/lihaoyi/macropy/blob/master/macropy/macros2/pyxl_strings.py) simply uses pyxl as a macro (operating on string literals), rather than hooking into the UTF-8 decoder. In general, this demonstrates how easy it is to integrate an "external" DSL into your python program: MacroPy handles all the intricacies of hooking into the interpreter and intercepting the import workflow. The programmer simply needs to provide the source-to-source transformation, which in this case was already provided.

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

print str(p)    #Point(1, 2)
print p.x       #1
print p.y       #2
print Point(1, 2) == Point(1, 2)
#True
```

[Case classes](http://www.codecommit.com/blog/scala/case-classes-are-cool) are classes with extra goodies:

- A nice `__str__` method is autogenerated
- An autogenerated constructor
- Structural equality by default

The reasoning being that although you may sometimes want complex, custom-built classes with custom features and fancy inheritance, very (very!) often you want a simple class with a constructor, pretty `__str__` and `__repr__` methods, and structural equality which doesn't inherit from anything. Case classes provide you just that, with an extremely concise declaration:

```python
@case
class Point(x, y): pass
```

As opposed to the equivalent class, written manually:

```python
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "Point(" + self.x + ", " + self.y + ")"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)
```

Whew, what a lot of boilerplate! This is clearly a pain to do, error prone to deal with, and violates [DRY](http://en.wikipedia.org/wiki/Don't_repeat_yourself) in an extreme way: each member of the class (`x` and `y` in this case) has to be repeated _6_ times, with loads and loads of boilerplate. It is also **wrong**, so see if you can spot the bug in it! Given how tedious writing all this code is, it is no surprise that most python classes do not come with proper `__str__` or useful `__eq__` functions! With case classes, there is no excuse, since all this will be generated for you.

Case classes also provide a convenient copy-constructor, which creates a shallow copy of the case class with modified fields, leaving the original unchanged:

```python
a = Point(1, 2)
b = a.copy(x = 3)
print a #Point(1, 2)
print b #Point(3, 2)
```

Like any other class, a case class may contain methods in its body:

```python
@case
class Point(x, y):
    def length(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

print Point(3, 4).length() #5
```

or class variables. The only restrictions are that only the `__init__`, `__repr__`, `___str__`, `__eq__` methods will be set for you, and it may not manually inherit from anything. Instead of manual inheritence, inheritence for case classes is defined by _nesting_, as shown below:

```python
@case
class List():
    def __len__(self):
        return 0

    def __iter__(self):
        return iter([])

    class Nil:
        pass

    class Cons(head, tail):
        def __len__(self):
            return 1 + len(self.tail)

        def __iter__(self):
            current = self

            while len(current) > 0:
                yield current.head
                current = current.tail

print isinstance(Cons(None, None), List)    # True
print isinstance(Nil(), List)               # True

my_list = Cons(1, Cons(2, Cons(3, Nil())))
empty_list = Nil()

print my_list.head              # 1
print my_list.tail              # Cons(2, Cons(3, Nil()))
print len(my_list)              # 5
print sum(iter(my_list))        # 6
print sum(iter(empty_list))     # 0
```

This is an implementation of a singly linked [cons list](http://en.wikipedia.org/wiki/Cons), providing both `head` and `tail` (LISP's `car` and `cdr`) as well as the ability to get the `len` or `iter` for the list.

As the classes `Nil` are `Cons` are nested within `List`, both of them get transformed into top-level classes which inherit from it. This nesting can go arbitrarily deep.

Pattern Matching
----------------
```python
@case
class List:
  def Nil():
    pass

  def Cons(x, xs):
    pass

def foldl1(my_list, op):
  with matching:
    if Cons(x, Nil()) << my_list:
      return x
    elif Cons(x, xs) << my_list:
      return op(x, foldl1(xs, op))
```

Pattern matching is taken from many functional languages, including Haskell,
ML, and Scala, all of which allow a convenient syntax for extracting elements
out of a complex data structure.  One can also override the way in which a
pattern is matched.

```python
class Twice(object):
  @classmethod
  def __unapply__(x):
    if not isinstance(x, int) or x % 2 != 0:
      raise PatternMatchException()
    else:
      return ([x/2], {})

with patterns:
  Twice(n) << 8
  print n     # 4
```


Tail-call Optimization
-----------
Work-in-progress

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
-------------
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

Parser Combinators
------------------
```python
def reduce_chain(chain):
    chain = list(reversed(chain))
    o_dict = {
        "+": f%(_+_),
        "-": f%(_-_),
        "*": f%(_*_),
        "/": f%(_/_),
    }
    while len(chain) > 1:
        a, [o, b] = chain.pop(), chain.pop()
        chain.append(o_dict[o](a, b))
    return chain[0]

"""
PEG Grammer:
Value   <- [0-9]+ / '(' Expr ')'
Op      <- "+" / "-" / "*" / "/"
Expr <- Value (Op Value)*
"""
with peg:
    value = '[0-9]+'.r // int | ('(', expr, ')') // (f%_[1])
    op = '+' | '-' | '*' | '/'
    expr = (value is first, (op, value).rep is rest) >> reduce_chain([first] + rest)

print expr.parse_all("123")             #[123]
print expr.parse_all("((123))")         #[123]
print expr.parse_all("(123+456+789)")   #[1368]
print expr.parse_all("(6/2)")           #[3]
print expr.parse_all("(1+2+3)+2")       #[8]
print expr.parse_all("(((((((11)))))+22+33)*(4+5+((6))))/12*(17+5)") #[1804]
```

[Parser Combinators](http://en.wikipedia.org/wiki/Parser_combinator) are a really nice way of building simple recursive descent parsers, when the task is too large for [regexes](http://en.wikipedia.org/wiki/Regex) but yet too small for the heavy-duty [parser generators](http://en.wikipedia.org/wiki/Comparison_of_parser_generators). These parser combinators are inspired by [Scala's](http://www.suryasuravarapu.com/2011/04/scala-parser-combinators-win.html), utilizing macros to make the syntax as clean as possible.

The above example describes a simple parser for arithmetic expressions, using our own parser combinator library which roughly follows the [PEG](http://en.wikipedia.org/wiki/Parsing_expression_grammar) syntax. Note how that in the example, the bulk of the code goes into the loop that reduces sequences of numbers and operators to a single number, rather than the recursive-descent parser itself!

Anything within a `with peg:` block is transformed into a *parser*. A parser is something with a `.parse_all(input)` method that attempts to parse the given `input` string. This method returns:

- `None`, if the parser failed to parse the input
- `[result]` if the parser succeeded with the value `result`

###Basic Combinators

Parsers are generally built up from a few common building blocks:

- String literals like `'+'` match the input to their literal value (e.g. '+') and return it as the parse result, or fails (returns `None`) if it does not match.
- Regexes like `'[0-9]+'.r` match the regex to the input if possible, and return it. Otherwise it fails.
- Tuples like `('(', expr, ')')` match each of the elements within sequentially, and return a list containing the result of each element. It fails if any of its elements fails.
- Elements separated by `|`, for example `'+' | '-' | '*' | '/'`, attempt to match each of the options from left to right, and return the result of the first success.
- Elements separated by `&`, for example `'[1234]'.r & '[3456]'.r`, require both sides succeed, and return the result of the left side.
- `parser.rep` attempts to match the `parser` 0 or more times, returning a list of the results from each successful match.
- `parser.rep1` attempts to match the `parser` 1 or more times, returning a list of the results from each successful match. If `parser` does not succeed at least once, `parser.rep1` fails.
- `-parser` negates the `parser`: if `parser` succeeded (with any result), `-parser` fails. If `parser` failed, `-parser` succeeds with the result `""`, the empty string.
- `parser * n` attempts to match the `parser` exactly `n` times, returning a list of length `n` containing the result of the `n` successes. Fails otherwise.
- `parser.opt` matches the `parser` 0 or 1 times, returning either `[]` or `[result]` where `result` is the result of `parser`.

###Transformers

So far, these building blocks all return the raw parse tree: all the things like whitespace, curly-braces, etc. will still be there. Often, you want to take a parser e.g.

```python
with peg:
    num = r('[0-9]+')

print num.parse_all("123") # ["123"]
```

which returns the a string of digits, and convert it into a parser which returns an `int` with the value of that string. This can be done with the `//` operator:

```python
with peg:
    num = r('[0-9]+') // int

print num.parse_all("123") # [123]
```

The `//` operator takes a function which will be used to transform the result of the parser: in this case, it is the function `int`, which transforms the returned string into an integer. Another example is:

```python
with peg:
    laugh = 'lol'
    laughs1 = 'lol'.rep1
    laughs2 = lots_of_laughs_1 // "".join

print laughs1.parse_all("lollollol") # [['lol', 'lol', 'lol]]
print laughs2.parse_all("lollollol") # ['lollollol]
```

Where the function `"".join"` is used to join together the list of results from `laughs1` into a single string.

Although `//` is sufficient for everyone's needs, it is not always convenient. In the example above, a `value` is defined to be:

```python
value = ... | ('(', expr, ')') // (lambda x: x[1])
```

As you can see, we need to strip off the unwanted parentheses from the parse tree, and we do it with a `lambda` that only selects the middle element, which is the result of the `expr` parser. An alternate way of representing this is:

```python
value = ... | ('(', expr is result, ')') >> result
```

In this case, the `is` keyword is used to bind the result of `expr` to the name `result`. The `>>` operator can be used to transform the parser by only operating on the *bound* results within the parser. This goes a long way to keep things neat. For example, a JSON parser may define an array to be:

```python
with peg:
    ...
    # parses an array and extracts the relevant bits into a Python list
     array = ('[', (json_exp, (',', json_exp).rep), opt(space), ']')//(lambda x: [x[1][0]] + [y[1] for y in x[1][1]])
    ...
```

Where the huge `lambda` is necessary to pull out the necessary parts of the parse tree into a Python list. Although it works, it's difficult to write correctly and equally difficult to read. Using the `is` operator, this can be rewritten as:

```python
array = ('[', json_exp is first, ~(',', json_exp is rest), opt(space), ']') >> [first] + rest
```

Now, it is clear that we are only interested in the result of the two `json_exp` parsers. The `>>` operator allows us to use those, while the rest of the parse tree (`[`s, `,`s, etc.) are conveniently discarded.

###Full Example
These parser combinators are not limited to toy problems, like the arithmetic expression parser above. Below is the full source of the JSON parser, along with it's PEG grammer:

```python
"""
JSON <- S? ( Object / Array / String / True / False / Null / Number ) S?

Object <- "{"
             ( String ":" JSON ( "," String ":" JSON )*
             / S? )
         "}"

Array <- "["
            ( JSON ( "," JSON )*
            / S? )
        "]"

String <- S? ["] ( [^ " \ U+0000-U+001F ] / Escape )* ["] S?

Escape <- [\] ( [ " / \ b f n r t ] / UnicodeEscape )

UnicodeEscape <- "u" [0-9A-Fa-f]{4}

True <- "true"
False <- "false"
Null <- "null"

Number <- Minus? IntegralPart FractionalPart? ExponentPart?

Minus <- "-"
IntegralPart <- "0" / [1-9] [0-9]*
FractionalPart <- "." [0-9]+
ExponentPart <- ( "e" / "E" ) ( "+" / "-" )? [0-9]+
S <- [ U+0009 U+000A U+000D U+0020 ]+
"""
with peg:
    json_exp = (space.opt, (obj | array | string | true | false | null | number) is exp, space.opt) >> exp

    pair = (string is k, ':', json_exp is v) >> (k, v)
    obj = ('{', pair is first, (',', pair is rest).rep, space.opt, '}') >> dict([first] + rest)
    array = ('[', json_exp is first, (',', json_exp is rest).rep, space.opt, ']') >> [first] + rest

    string = (space.opt, '"', ('[^"]'.r | escape).rep // ("".join) is body, '"') >> "".join(body)
    escape = '\\', ('"' | '/' | '\\' | 'b' | 'f' | 'n' | 'r' | 't' | unicode_escape)
    unicode_escape = 'u', '[0-9A-Fa-f]'.r * 4

    true = 'true' >> True
    false = 'false' >> False
    null = 'null' >> None

    number = (minus.opt, integral, fractional.opt, exponent.opt) // (f%float("".join(_)))
    minus = '-'
    integral = '0' | '[1-9][0-9]*'.r
    fractional = ('.', '[0-9]+'.r) // "".join
    exponent = (('e' | 'E'), ('+' | '-').opt, "[0-9]+".r) // "".join

    space = '\s+'.r

test_string = """
    {
        "firstName": "John",
        "lastName": "Smith",
        "age": 25,
        "address": {
            "streetAddress": "21 2nd Street",
            "city": "New York",
            "state": "NY",
            "postalCode": 10021
        },
        "phoneNumbers": [
            {
                "type": "home",
                "number": "212 555-1234"
            },
            {
                "type": "fax",
                "number": "646 555-4567"
            }
        ]
    }
"""

import json
print json_exp.parse_all(test_string)[0] == json.loads(test_string)
# True

import pprint
pp = pprint.PrettyPrinter(4)
pp.pprint(parser.parse_all(string)[0])
#{   'address': {   'city': 'New York',
#                   'postalCode': 10021.0,
#                   'state': 'NY',
#                   'streetAddress': '21 2nd Street'},
#    'age': 25.0,
#    'firstName': 'John',
#    'lastName': 'Smith',
#    'phoneNumbers': [   {   'number': '212 555-1234', 'type': 'home'},
#                        {   'number': '646 555-4567', 'type': 'fax'}]}
```

As you can see, the full parser parses that non-trivial blob of JSON into an identical structure as the in-built `json` package. In addition, the source of the parser looks almost identical to the PEG grammar it is parsing, shown above. Pretty neat!

Credits
=======

The MIT License (MIT)

Copyright (c) 2013, Li Haoyi, Justin Holmgren

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
