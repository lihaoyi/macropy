.. _peg:

MacroPEG Parser Combinators
---------------------------

.. code:: python

  from macropy.peg import macros, peg
  from macropy.quick_lambda import macros, f

  """
  PEG grammar from Wikipedia

  Op      <- "+" / "-" / "*" / "/"
  Value   <- [0-9]+ / '(' Expr ')'
  Expr <- Value (Op Value)*

  Simplified to remove operator precedence
  """
  def reduce_chain(chain):
      chain = list(reversed(chain))
      o_dict = {
          "+": f[_+_],
          "-": f[_-_],
          "*": f[_*_],
          "/": f[_/_],
      }
      while len(chain) > 1:
          a, [o, b] = chain.pop(), chain.pop()
          chain.append(o_dict`o <a, b>`_)
      return chain[0]

  with peg:
      op = '+' | '-' | '*' | '/'
      value = '[0-9]+'.r // int | ('(', expr, ')') // f[_[1]]
      expr = (value, (op, value).rep is rest) >> reduce_chain([value] + rest)

  print(expr.parse("123"))             # 123
  print(expr.parse("((123))"))         # 123
  print(expr.parse("(123+456+789)"))   # 1368
  print(expr.parse("(6/2)"))           # 3
  print(expr.parse("(1+2+3)+2"))       # 8
  print(expr.parse("(((((((11)))))+22+33)*(4+5+((6))))/12*(17+5)"))    # 1804


MacroPEG is an implementation of `Parser Combinators`__, an approach
to building recursive descent parsers, when the task is too large for
`regexes`__ but yet too small for the heavy-duty `parser
generators`__. MacroPEG is inspired by Scala's `parser combinator
library`__, utilizing python macros to make the syntax as clean as
possible .

__ http://en.wikipedia.org/wiki/Parser_combinator
__ http://en.wikipedia.org/wiki/Regex
__ http://en.wikipedia.org/wiki/Comparison_of_parser_generators
__ http://www.suryasuravarapu.com/2011/04/scala-parser-combinators-win.html

The above example describes a simple parser for arithmetic
expressions, which roughly follows the `PEG`__ syntax. Note how that
in the example, the bulk of the code goes into the loop that reduces
sequences of numbers and operators to a single number, rather than the
recursive-descent parser itself!

__ http://en.wikipedia.org/wiki/Parsing_expression_grammar


Any assignment (``xxx = ...``) within a ``with peg:`` block is
transformed into a ``Parser``. A ``Parser`` comes with a
``.parse(input)`` method, which returns the parsed result if parsing
succeeds and raises a ``ParseError`` in the case of failure. The
``ParseError`` contains a nice human-readable string detailing exactly
what went wrong.

.. code:: python

  json_exp.parse('{"omg": "123", "wtf": , "bbq": "789"}')
    # ParseError: index: 22, line: 1, col: 23
    # json_exp / obj / pair / json_exp
    # {"omg": "123", "wtf": , "bbq": "789"}
    #                       ^
    # expected: (obj | array | string | true | false | null | number)


In addition to ``.parse(input)``, a Parser also contains:

- ``parse_string(input)``, a more program-friendly version of ``parse``
  that returns successes and failures as boxed values (with metadata);

- a ``parse_partial(input)`` method, which is identical to
  ``parse_string``, but does not require the entire ``input`` to be
  consumed, as long as some prefix of the ``input`` string matches. The
  ``remaining`` attribute of the ```Success```  indicates how far into the
  ``input`` string parsing proceeded.

Basic Combinators
~~~~~~~~~~~~~~~~~

Parsers are generally built up from a few common building blocks. The
fundamental atoms include:

- string literals like ``'+'`` match the input to their literal value
  (e.g. '+') and return it as the parse result, or fails if it does
  not match;

- regexes like ``'[0-9]+'.r`` match the regex to the input if possible,
  and return it;
- tuples like ``('(', expr, ')')`` match each of the elements within
  sequentially, and return a list containing the result of each
  element. It fails if any of its elements fails;
- parsers separated by ``|``, for example ``'+' | '-' | '*' | '/'``,
  attempt to match each of the alternatives from left to right, and
  return the result of the first success;
- parsers separated by ``&``, for example ``'[1234]'.r & '[3456]'.r``,
  require both parsers succeed, and return the result of the left
  side;
- ``parser.rep`` attempts to match the ``parser`` 0 or more times,
  returning a list of the results from each successful match;
- ``-parser`` negates the ``parser``: if ``parser`` succeeded (with any
  result), ``-parser`` fails. If ``parser`` failed, ``-parser`` succeeds
  with the result ``""``, the empty string.

Apart from the fundamental atoms, MacroPeg also provides combinators
which are not strictly necessary, but are nevertheless generally
useful in almost all parsing scenarios:

- ``parser.rep1`` attempts to match the ``parser`` 1 or more times,
  returning a list of the results from each successful match. If
  ``parser`` does not succeed at least once, ``parser.rep1``
  fails. Equivalent to ``parser.rep & parser``;
- ``parser.rep_with(other)`` and ``parser.rep1_with(other)`` repeat the
  ``parser`` 0 or more or 1 or more times respectively, except now the
  ``other`` parser is invoked in between invocations of ``parser``. The
  output of ``other`` is discarded, and these methods return a list of
  values similar to ``rep`` and ``rep1``;
- ``parser * n`` attempts to match the ``parser`` exactly ``n`` times,
  returning a list of length ``n`` containing the result of the ``n``
  successes. Fails otherwise;
- ``parser.opt`` matches the ``parser`` 0 or 1 times, returning either
  ``[]`` or ``[result]`` where ``result`` is the result of
  ``parser``. Equivalent to ``parser | Succeed([])``;
- ``parser.join`` takes a parser that returns a list of strings
  (e.g. tuples, ``rep``, ``rep1``, etc.) and returns a parser which
  returns the strings concatenated together. Equivalent to ``parser //
  "".join``.

Transforming values using ``//``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

So far, these building blocks all return the raw parse tree: all the
things like whitespace, curly-braces, etc. will still be there. Often,
you want to take a parser e.g.

.. code:: python

  from macropy.peg import macros, peg
  with peg:
      num = '[0-9]+'.r

  print(repr(num.parse("123"))) # '123'


which returns a string of digits, and convert it into a parser which
returns an ``int`` with the value of that string. This can be done
with the ``//`` operator:

.. code:: python

  from macropy.peg import macros, peg
  with peg:
      num = '[0-9]+'.r // int

  print(repr(num.parse("123"))) # 123


The ``//`` operator takes a function which will be used to transform
the result of the parser: in this case, it is the function ``int``,
which transforms the returned string into an integer.

Another example is:

.. code:: python

  with peg:
      laugh = 'lol'
      laughs1 = 'lol'.rep1
      laughs2 = laughs1 // "".join

  print(laughs1.parse("lollollol")) # ['lol', 'lol', 'lol]
  print(laughs2.parse("lollollol")) # lollollol


Where the function ``"".join"`` is used to join together the list of
results from ``laughs1`` into a single string. As mentioned earlier,
``laughs2`` can also be written as ``laughs2 = laughs1.join``.

Binding Values using ``>>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Although ``//`` is sufficient for everyone's needs, it is not always
convenient. In the example above, a ``value`` is defined to be:

.. code:: python

  value = ... | ('(', expr, ')') // (lambda x: x[1])


As you can see, we need to strip off the unwanted parentheses from the
parse tree, and we do it with a ``lambda`` that only selects the
middle element, which is the result of the ``expr`` parser. An
alternate way of representing this is:

.. code:: python

  value = ... | ('(', expr is result, ')') >> result


In this case, the ``is`` keyword is used to bind the result of
``expr`` to the name ``result``. The ``>>`` ("bind") operator can be
used to transform the parser by only operating on the *bound* results
within the parser. ``>>`` also binds the results of *other parsers* to
their name. Hence the above is equivalent to:

.. code:: python

  value = ... | ('(', expr, ')') >> expr


The ``expr`` on the left refers to the parser named ``expr`` in the
``with peg:`` block, while the ``expr`` on the right refers to the
*results of the parser named* ``expr`` *in case of a successful
parse*. The parser on the left has to be outside any ``is``
expressions for it to be captured as above, and so in this line in the
above parser:

.. code:: python

  expr = (value, (op, value).rep is rest) >> reduce_chain([value] + rest)


The result of the first ``value`` on the left of ``>>`` is bound to
``value`` on the right, while the second ``value`` is not because it
is within an ``is`` expression bound to the name ``rest``. If you have
multiple parsers of the same name on the left of ``>>``, you can
always refer to each individual explicitly using the ``is`` syntax
shown above.

Althought this seems like a lot of shuffling variables around and
meddling with the local scope and semantics, it goes a long way to
keep things neat. For example, a JSON parser may define an array to
be:

.. code:: python

  with peg:
      ...
      # parses an array and extracts the relevant bits into a Python list
       array = ('[', (json_exp, (',', json_exp).rep), space.opt, ']') // (lambda x: [x[1][0]] + [y[1] for y in x[1][1]])
      ...


Where the huge ``lambda`` is necessary to pull out the necessary parts
of the parse tree into a Python list. Although it works, it's
difficult to write correctly and equally difficult to read. Using the
``is`` operator, this can be rewritten as:

.. code:: python

  array = ('[', json_exp is first, (',', json_exp is rest).rep, space.opt, ']') >> [first] + rest


Now, it is clear that we are only interested in the result of the two
``json_exp`` parsers. The ``>>`` operator allows us to use those,
while the rest of the parse tree (``[``, ``,``, etc.) are conveniently
discarded. Of course, one could go a step further and us the
``rep_with`` method which is intended for exactly this purpose:

.. code:: python

  array = ('[', json_exp.rep_with(',') >> arr, space.opt, ']') >> arr


Which arguably looks the cleanest of all!

Cut
~~~

.. code:: python

  from macropy.peg import macros, peg, cut
  with peg:
      expr1 = ("1", "2", "3") | ("1", "b", "c")
      expr2 = ("1", cut, "2", "3") | ("1", "b", "c")

  print(expr1.parse("1bc") # ['1', 'b', 'c'])
  print(expr2.parse("1bc"))
  # ParseError: index: 1, line: 1, col: 2
  # expr2
  # 1bc
  #  ^
  # expected: '2'


``cut`` is a special token used in a sequence of parsers, which
commits the parsing to the current sequence. As you can see above,
without ``cut``, the left alternative fails and the parsing then
attempts the right alternative, which succeeds. In contrast, with
``expr2``, the parser is committed to the left alternative once it
reaches the ``cut`` (after successfully parsing "1") and thus when the
left alternative fails, the right alternative is not tried and the
entire ``parse`` fails.

The purpose of ``cut`` is two-fold:

Increasing performance by removing unnecessary backtracking
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Using JSON as an example: if your parser sees a `{`, begins parsing a
JSON object, but some time later it fails, it does not need to both
backtracking and attempting to parse an Array (``[...``), or a String
(``"...``), or a Number. None of those could possibly succeed, so
cutting the backtracking and failing fast prevents this unnecessary
computation.

Better error reporting.
+++++++++++++++++++++++

For example, if you try to parse the JSON String;

.. code:: javascript

  {        : "failed lol"}


if your JSON parser looks like:

.. code:: python

  with peg:
      ...
      json_exp = obj | array | string | num | true | false | null
      obj = '{', pair.rep_with(",") , space, '}'
      ...


Without ``cut``, the only information you could gain from attempting to
parse that is something like:

.. code::

  index: 0, line: 1, col: 1
  json_exp
  {    : 1, "wtf": 12.4123}
  ^
  expected: (obj | array | string | true | false | null | number)


On the other hand, using a ``cut`` inside the ``object`` parser
immediately after parsing the first ``{``, we could provide a much
more specific error:

.. code::

  index: 5, line: 1, col: 6
  json_exp / obj
  {    : 1, "wtf": 12.4123}
       ^
  expected: '}'


In the first case, after failing to parse ``obj``, the ``json_exp``
parser goes on to try all the other alternatives. After all to them
fail to parse, it only knows that trying to parse ``json_exp``
starting from character 0 doesn't work; it has no way of knowing that
the alternative that was "supposed" to work was ``obj``.

In the second case, ``cut`` is inserted inside the ``object`` parser,
something like:

.. code:: python

  obj = '{', cut, pair.rep_with(",") , space, '}'


Once the first ``{`` is parsed, the parser is committed to that
alternative. Thus, when it fails to parse ``string``, it knows it
cannot backtrack and can immediately end the parsing. It can now give
a much more specific source location (character 10) as well as better
information on what it was trying to parse (``json / object /
string``).

Full Example
~~~~~~~~~~~~


MacroPEG is not limited to toy problems, like the arithmetic
expression parser above. Below is the full source of a JSON parser,
provided in the `unit tests`__:

__ macropy/experimental/test/peg.py

.. code:: python

  from macropy.peg import macros, peg, cut
  from macropy.quick_lambda import macros, f

  def decode(x):
      x = x.decode('unicode-escape')
      try:
          return str(x)
      except:
          return x

  escape_map = {
      '"': '"',
      '/': '/',
      '\\': '\\',
      'b': '\b',
      'f': '\f',
      'n': '\n',
      'r': '\r',
      't': '\t'
  }

  """
  Sample JSON PEG grammar for reference, shameless stolen from
  https://github.com/azatoth/PanPG/blob/master/grammars/JSON.peg

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

  Number <- Minus? IntegralPart fractPart? expPart?

  Minus <- "-"
  IntegralPart <- "0" / [1-9] [0-9]*
  fractPart <- "." [0-9]+
  expPart <- ( "e" / "E" ) ( "+" / "-" )? [0-9]+
  S <- [ U+0009 U+000A U+000D U+0020 ]+
  """
  with peg:
          json_doc = (space, (obj | array), space) // f[_[1]]
          json_exp = (space, (obj | array | string | true | false | null | number), space) // f[_[1]]

          pair = (string is k, space, ':', cut, json_exp is v) >> (k, v)
          obj = ('{', cut, pair.rep_with(",") // dict, space, '}') // f[_[1]]
          array = ('[', cut, json_exp.rep_with(","), space, ']') // f[_[1]]

          string = (space, '"', (r'[^"\\\t\n]'.r | escape | unicode_escape).rep.join is body, '"') >> "".join(body)
          escape = ('\\', ('"' | '/' | '\\' | 'b' | 'f' | 'n' | 'r' | 't') // escape_map.get) // f[_[1]]
          unicode_escape = ('\\', 'u', ('[0-9A-Fa-f]'.r * 4).join).join // decode

          true = 'true' >> True
          false = 'false' >> False
          null = 'null' >> None

          number = decimal | integer
          integer = ('-'.opt, integral).join // int
          decimal = ('-'.opt, integral, ((fract, exp).join) | fract | exp).join // float

          integral = '0' | '[1-9][0-9]*'.r
          fract = ('.', '[0-9]+'.r).join
          exp = (('e' | 'E'), ('+' | '-').opt, "[0-9]+".r).join

          space = '\s*'.r


Testing it out with some input, we can see it works as we would
expect:

.. code:: python

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
  print(json_exp.parse(test_string) == json.loads(test_string))
  # True

  import pprint
  pp = pprint.PrettyPrinter(4)
  pp.pprint(json_exp.parse(test_string))
  #{   'address': {   'city': 'New York',
  #                   'postalCode': 10021.0,
  #                   'state': 'NY',
  #                   'streetAddress': '21 2nd Street'},
  #    'age': 25.0,
  #    'firstName': 'John',
  #    'lastName': 'Smith',
  #    'phoneNumbers': [   {   'number': '212 555-1234', 'type': 'home'},
  #                        {   'number': '646 555-4567', 'type': 'fax'}]}


You can see that ``json_exp`` parses that non-trivial blob of JSON into
an identical structure as Python's in-built ``json`` package. In
addition, the source of the parser looks almost identical to the PEG
grammar it is parsing, shown above. This parser makes good use of the
``//`` and ``>>`` operators to transform the output of its individual
components, as well as using ``rep_with`` method to easily parse the
comma-separated JSON objects and arrays. This parser is almost fully
compliant with the `test cases <http://www.json.org/JSON_checker/>`_
found on the `json.org <www.json.org>`_ website (it doesn't fail, as
it should, for deeply-nested JSON arrays), which isn't bad for 50
lines of code.

As mentioned earlier, MacroPEG parsers also provide exceptions with
nice error messages when the ``parse`` method fails, and the JSON parser
is no exception. Even when parsing larger documents, the error
reporting rises to the challenge:

.. code:: python

  json_exp.parse("""
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
                  "number": 646 555-4567"
              }
          ]
      }
  """)

  # ParseError: index: 456, line: 19, col: 31
  # json_exp / obj / pair / json_exp / array / json_exp / obj
  #                 "number": 646 555-4567"
  #                               ^
  # expected: '}'


Pretty neat! This full example of a JSON parser demonstrates what
MacroPEG provides to a programmer trying to write a parser:

- Excellent error reporting
- Simple AST processing, on the fly
- An extremely clear PEG-like syntax
- Extremely concise parser definitions

Not bad for an implementation that spans :repo:`350 lines of code
<macropy/peg.py>`!
