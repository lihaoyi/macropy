.. _hygienic_macro:

Making your Macros Hygienic
---------------------------

In `first_macro`:ref:, we went
through how the use basic tools such as quasiquotes and Walkers in
order to perform simple AST transforms. In this section, we will go
through the shortcomings of doing the naive transforms, and how to use
hygiene to make your macros more robust.

`Hygienic`__ macros are macros which will not accidentally `shadow`__
an identifier, or have the identifiers they introduce shadowed by user
code. For example, the `quicklambda`:ref: macro takes this:

__ http://en.wikipedia.org/wiki/Hygienic_macro
__ http://en.wikipedia.org/wiki/Variable_shadowing

.. code:: python

  func = f[_ + 1]
  print(func(1))
  # 2

And turns it into a lambda expression. If we did it naively, like we
did in the `first_macro`:ref:, we may expand it into this:

.. code:: python

  func = lambda arg0: arg0 + 1
  print(func(1))
  # 2


However, if we introduce a variable called ``arg0`` in the enclosing scope:

.. code:: python

  arg0 = 10
  func = f[_ + arg0]
  print(func(1))
  # 2
  # should print 11


It does not behave as we may expect; we probably want it to produce
``11``. this is because the ``arg0`` identifier introduced by the
``f`` macro shadows the ``arg0`` in our enclosing scope. These bugs
could be hard to find, since renaming variables could make them appear
or disappear. Try executing the code in
`docs/examples/hygiene/hygiene_failures`:repo: and to see this for
your self.

gen_sym
~~~~~~~

There is a way out of this: if you create a new variable, but use an
identifier that has not been used before, you don't stand the risk of
accidentally shadowing something you didn't intend to. To help with
this, MacroPy provides the ``gen_sym`` function, which you can acquire
by adding an extra parameter named ``gen_sym`` to your macro definition:

.. code:: python

  @macros.expr
  def f(tree, gen_sym, **kw):
      ...
      new_name = gen_sym()
      ... use new_name ...


``gen_sym`` is a function which produce a new identifier (as a string)
every time it is called. This is guaranteed to produce a identifier
that does not appear anywhere in the original source code, or have
been produced by an earlier call to ``gen_sym``. You can thus use
these identifiers without worrying about shadowing an identifier
someone was using; the full code for this is given in
`docs/examples/hygiene/gen_sym`:repo:, so check it out and try
executing it to see it working

Hygienic Quasiquotes
~~~~~~~~~~~~~~~~~~~~

Let's look at another use case: the implementation of the various
`tracing`:ref: macros. These macros generally can't rely solely
on AST transforms, but also require runtime support in order to
operate. Consider a simple ``log`` macro:

.. code:: python

  # macro_module.py
  from macropy.core.macros import Macros
  from macropy.core.quotes import macros, q, u, ast_literal

  macros = Macros()

  @macros.expr
  def log(tree, exact_src, **kw):
      new_tree = q[wrap(u[exact_src(tree)], ast_literal[tree])]
      return new_tree

  def wrap(txt, x):
      print(txt + " -> " + repr(x))
      return x


This macro aims to perform a conversion like:

.. code:: python

  log[1 + 2 + 3] -> wrap("1 + 2 + 3", 1 + 2 + 3)


Where the ``wrap`` function then prints out both the source code and the
``repr`` of the logged expression. This is but a single example of the
myriad of things that expanded macros may need at run time.

Naively performing this transform runs into problems:

.. code:: python

  from macro_module import macros, log


  log[1 + 2 + 3]
  # NameError: name 'wrap' is not defined


This is because although ``wrap`` is available in ``macro_module.py``, it
is not available in ``test.py``. Hence the expanded code fails when it
tries to reference ``wrap``. There are several ways which this can be
accomplished:

Manual Imports
~~~~~~~~~~~~~~

.. code:: python

  # test.py
  from macro_module import macros, log, wrap

  log[1 + 2 + 3]
  # 1 + 2 + 3 -> 6


You can simply import ``wrap`` from ``macro_module.py`` into ``test.py``,
along with the ``log`` macro itself. This way, the expanded code has a
``wrap`` function that it can call. Although this works in this example,
it is somewhat fragile in the general case, as the programmer could
easily accidentally create a variable named ``wrap``, not knowing that
it was being used by ``log`` (after all, you can't see it used anywhere
in the source code!), causing it to fail:

.. code:: python

  # test.py
  from macro_module import macros, log, wrap

  wrap = "chicken salad"

  log[1 + 1]
  # TypeError: 'str' object is not callable


Alternately, the programmer could simply forget to import it, for the
same reason:

.. code:: python

  # test.py
  from macro_module import macros, log

  log[1 + 1]
  # NameError: name 'wrap' is not defined


which gives a rather confusing error message: ``wrap`` is not defined?
From the programmer's perspective, ``wrap`` isn't used at all! These
very common pitfalls mean you should probably avoid this approach in
favor of the latter two.

``hq``
~~~~~~

.. code:: python

  # macro_module.py
  from macropy.core.macros import Macros
  from macropy.core.quotes import macros, ast_literal
  from macropy.core.hquotes import macros, hq, u

  macros = Macros()

  @macros.expr
  def log(tree, exact_src, **kw):
      new_tree = hq[wrap(u[exact_src(tree)], ast_literal[tree])]
      return new_tree

  def wrap(txt, x):
      print(txt + " -> " + repr(x))
      return x

.. code:: python

  # test.py
  from macro_module import macros, log

  wrap = 3 # try to confuse it

  log[1 + 2 + 3]
  # 1 + 2 + 3 -> 6
  # it still works despite trying to confuse it with `wrap`


The important changes in this snippet, as compared to the previous,
are:

- The removal of ``wrap`` from the import statement.
- Replacement of ``q`` with ``hq``

``hq`` is the hygienic quasiquote macro. Unlike traditional
quasiquotes (``q``), ``hq`` jumps through some hoops in order to
ensure that the ``wrap`` you are using inside the ``hq[...]``
expression really-truly refers to the ``wrap`` that is in scope *at
the macro definition point*, not at tbe macro expansion point (as
would be the case using the normal ``q`` macro). The end-result is
that ``wrap`` refers to the ``wrap`` you want in ``macro_module.py``,
and not whatever ``wrap`` happened to be defined in ``test.py``. See
`docs/examples/hygiene/hygienic_quasiquotes`:repo: to see it working.

In general, ``hq`` allows you to refer to anything that is in scope
where ``hq`` is being used. Apart from module-level global variables
and functions, this includes things like locally scoped variables,
which will be properly saved so they can be referred to later even
when the macro has completed:

.. code:: python

  # macro_module.py
  @macros.block
  def expand(tree, gen_sym, **kw):
      v = 5
      with hq as new_tree:
          return v
      return new_tree

.. code:: python

  # test.py
  def run():
      x = 1
      with expand:
          pass

  print(run()) # prints 5


In this case, the value of ``v`` is captured by the ``hq``, such that even
when ``expand`` has returned, it can still be used to return ``5`` to the
caller of the ``run()`` function.

Breaking Hygiene
~~~~~~~~~~~~~~~~

By default, all top-level names in the ``hq[...]`` expression (this
excludes things like the contents of ``u[]`` ``name[]``
``ast_literal[]`` unquotes) are hygienic, and are bound to the
variable of that name at the macro definition point. This means that
if you want a name to bind to some variable *at the macro expansion
point*, you can always manually break hygiene by using the ``name[]``
or ``ast_literal[]`` unquotes. The ``hq`` macro also provides an
``unhygienic[...]`` unquote just to streamline this common
requirement:

.. code:: python

  @macros.block
  def expand(tree, gen_sym, **kw):
      v = 5
      with hq as new_tree:
          # all these do the same thing, and will refer to the variable named
          # 'v' whereever the macro is expanded
          return name["v"]
          return ast_literal[Name(id="v")]
          return unhygienic[v]
      return new_tree


Although all these do the same thing, you should prefer to use
``unhygienic[...]`` as it makes the intention clearer than using
``name[...]`` or ``ast_literal[...]`` with hard-coded strings.

``expose_unhygienic``
~~~~~~~~~~~~~~~~~~~~~

Going back to the ``log`` example:

.. code:: python

  # macro_module.py
  from macropy.core.macros import Macros
  from macropy.core.quotes import macros, ast_literal
  from macropy.core.hquotes import macros, hq, u, unhygienic

  macros = Macros()

  @macros.expr
  def log(tree, exact_src, **kw):
      new_tree = hq[wrap(unhygienic[log_func], u[exact_src(tree)], ast_literal[tree])]
      return new_tree


  def wrap(printer, txt, x):
      printer(txt + " -> " + repr(x))
      return x

  @macros.expose_unhygienic
  def log_func(txt):
      print(txt)


``expose_unhygienic`` is a hybrid between manual importing and
``hq``. Like manual importing, decorating functions with
``expose_unhygienic`` causes them to be imported under their
un-modified name, meaning they can shadow and be shadowed by other
identifiers in the macro-expanded code. Like ``expose``, it does not
require the source file using the macros to put the identifier in the
import list. This helps match what users of the macro expect: since
the name doesn't ever appear anywhere in the source, it doesn't make
sense for the macro to require the name being imported to work.

In this example, the ``log`` macro uses ``expose_unhygienic`` on a
``log_func`` function. The macro-expanded code by default will capture
the ``log_func`` function imported from ``macro_module.py``, which
prints the log to the console:

.. code:: python

  # test.py
  from macro_module import macros, log

  log[1 + 1]
  # 1 + 1 -> 2


But a user can intentionally shadow ``log_func`` in order to redirect
the logging, for example to a list

.. code:: python

  # test.py
  from macro_module import macros, log

  buffer = []
  def log_func(txt):
      buffer.append(txt)

  log[1 + 2 + 3]
  log[1 + 2]
  # doesn't print anything

  print(buffer)
  # ['1 + 2 + 3 -> 6', '1 + 2 -> 3']


See `docs/examples/hygiene/unhygienic`:repo: to see this example in
action. In general, ``expose_unhygienic`` is useful when you want the
macro to use a name that can be intentionally shadowed by the
programmer using the macro, allowing the programmer to implicitly
modify the behavior of the macro via this shadowing.

----------------------------------------

This section has covered how to use the various tools available
(``gen_sym``, ``hq``, ``expose_unhygienic``) in order to carefully
control the scoping and variable binding in the code generated by
macros. See the section on `hygiene`:ref: for a more detailed
explanation of what's going on behind the scenes.
