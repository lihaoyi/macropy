.. warning::

  Be aware that for what concerns MacroPy3 this macro hadn't been
  updated due to the external dependency lacking compatibility with
  Python 3.

.. _js:

JS Snippets
------------

.. code:: python

  from macropy.experimental.javascript import macros, pyjs

  code, javascript = pyjs[lambda x: x > 5 and x % 2 == 0]

  print(code)
  # <function <lambda> at 0x0000000003515C18>

  print(javascript)
  # $def(function $_lambda(x) {return $b.bool($b.do_ops(x, '>', 5)) && $b.bool($b.do_ops($b.mod(x, 2), '==', 0));})

  for i in range(10):
      print(i, code(i), self.exec_js_func(javascript, i))

  # 0 False False
  # 1 False False
  # 2 False False
  # 3 False False
  # 4 False False
  # 5 False False
  # 6 True True
  # 7 False False
  # 8 True True
  # 9 False False


JS Snippets is a macro that allows you to mark out sections of code
that will be cross-compiled into Javascript at module-import
time. This cross-compilation is done using `PJs
<https://github.com/jabapyth/PJs>`_. The generated Javascript is
incredibly ugly, thanks in part to the fact that in order to preserve
semantics in the presence of features that Python has but JS lacks
(such as `operator overloading
<http://en.wikipedia.org/wiki/Operator_overloading>`_), basically
every operation in the Javascript program has to be virtualized into a
method call. The translation also breaks down around the fringes of
the Python language.

Nonetheless, as the abov<e example demonstrates, the translation is
entirely acceptable for simple logic. Furthermore, with macros,
marking out snippets of Python code to be translated is as simple as
prepending either:

- ``js``, if you only want to translate the enclosed python expression
  into Javascript;
- ``pyjs``, if you want both the original expression as well as the
  translated Javascript (as in the example above). This is given to
  you as a tuple.

``pyjs`` is particularly interesting, because it brings us closer to the
holy grail of HTML form validation: having validation run on both
client and server, but still only be expressed once in the code
base. With ``pyjs``, it is trivial to fork an expression (such as the
conditional function shown above) into both Python and Javascript
representations. Rather than using a `menagerie
<https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/Forms/Data_form_validation?redirectlocale=en-US&redirectslug=HTML%2FForms%2FData_form_validation>`_
of `ad-hoc <http://docs.jquery.com/Plugins/validation>`_ `mini-DSLs
<https://code.google.com/p/validation-js/wiki/MainDocumentation>`_,
this lets you write your validation logic in plain Python.

As mentioned earlier, JS Snippets isn't very robust, and the
translation is full of bugs:

.. code:: python

  # these work
  assert self.exec_js(js[10]) == 10
  assert self.exec_js(js["i am a cow"]) == "i am a cow"

  # these literals are buggy, and it seems to be PJs' fault
  # ??? all the results seem to turn into strings ???
  assert self.exec_js(js(3.14)) == 3.14 # Fails
  assert self.exec_js(js[[1, 2, 'lol']]) == [1, 2, 'lol'] # Fails
  assert self.exec_js(js[{"moo": 2, "cow": 1}]) == {"moo": 2, "cow": 1} # Fails

  # set literals aren't supported so this throws an exception at
  # macro-expansion time
  # self.exec_js(js[{1, 2, 'lol'}])


Even as such basic things fail, other, more complex operations work
flawlessly:

.. code:: python

  script = js[sum([x for x in range(10) if x > 5])]
  print(script)
  # "$b.sum($b.listcomp([$b.range(10)], function (x) {return x;}, [function (x) { return $b.do_ops(x, '>', 5); }]))"
  print(self.exec_js(script))
  # 30


Here's another, less trivial use case: cross compiling a function that
searches for the `prime numbers
<http://en.wikipedia.org/wiki/Prime_number>`_:

.. code:: python

  code, javascript = pyjs[lambda n: [
      x for x in range(n)
      if 0 == len([
          y for y in range(2, x-2)
          if x % y == 0
      ])
  ]]
  print(code(20))
  # [0, 1, 2, 3, 4, 5, 7, 11, 13, 17, 19]
  print(self.exec_js_func(javascript, 20)))
  # [0, 1, 2, 3, 4, 5, 7, 11, 13, 17, 19]


These examples are all taken from the `unit tests`__.

__ macropy/experimental/test/js_snippets.py

Like `pinq`:ref:, JS Snippets
demonstrates the feasibility, the convenience of being able to mark
out sections of code using macros, to be cross-compiled into another
language and run remotely. Unlike PINQ, which is built on top of the
stable, battle-tested and widely used `SQLAlchemy
<http://www.sqlalchemy.org/>`_ library, JS Snippets is built on top of
an relatively unknown and untested Python to Javascript
cross-compiler, making it far from production ready.

Nonetheless, JS Snippets demonstrate the promise of being able to
cross-compile bits of your program and being able to run parts of it
remotely. The code which performs the integration of PJs and MacroPy
is a scant :repo:`25 lines long <macropy/experimental/js_snippets.py>`. If
a better, more robust Python to Javascript cross-compiler appears some
day, we could easily make use of it to provide a stable, seamless
developer experience of sharing code between (web) client and server.
