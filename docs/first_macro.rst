.. _first_macro:

Writing Your First Macro
------------------------

Now, we will go through what it takes to write a simple macro, with
some `self-contained examples <docs/examples>`:repo:. To begin, we need
three files

.. code:: python

  # run.py
  # target.py
  # macro_module.py


As mentioned earlier, you cannot use macros in the ``__main__`` module
(the file that is run directly via ``python ...``) and so we have to
have a separate bootstrap file ``run.py``, which will then execute
``target.py``, which contains macros defined in ``macro_module.py``.

.. code:: python

  # run.py
  import macropy.activate
  import target

  # target.py
  # macro_module.py


Now, let us define a simple macro, in ``macro_module.py``

.. code:: python

  # run.py
  import macropy.activate
  import target

  # target.py
  from macro_module import macros, expand

  print(expand[1 + 2])

  # macro_module.py
  from macropy.core.macros import Macros

  macros = Macros()

  @macros.expr
  def expand(tree, **kw):
      return tree


Running this via ``python run.py`` will print out ``3``; so far
``expand`` is a simple no-op macro which does not do anything to the
tree it is passed. This macro is provided in
`docs/examples/first_macro/nop`:repo: if you want to try it out
yourself; you can run it from the project root via ``python
docs/examples/first_macro/nop/run.py``.

The ``**kw`` serves to absorb all the arguments that you did not
declare. The macro can take additional arguments (not shown here)
which are documented `below`:ref:. Alternately, you can just
take a look at what the ``**kw`` dictionary contains.

The line

.. code:: python

  from macro_module import macros, expand


is necessary to declare what macros you want to use (``expand``), and
which module you want to load them from ``macro_module``. Aliases also
work:

.. code:: python

  from macro_module import macros, expand as my_alias

  print(my_alias[1 + 2])


As you would expect. Import-alls like ``from macro_module import *`` do
**not** work.

At this point, you can print out the tree you are receiving in various
forms just to see what you're getting:

.. code:: python

  # macro_module.py
  from macropy.core.macros import Macros

  macros = Macros()

  @macros.expr
  def expand(tree, **kw):
      print(tree)
      print(real_repr(tree))
      print(unparse(tree))
      return tree


When you run ``run.py``, This will print:

.. code:: python

  <_ast.BinOp object at 0x000000000206BBA8>
  BinOp(Num(1), Add(), Num(2))
  (1 + 2)
  3


As you can see, the AST objects don't have a nice ``__repr__``, but if
you use the MacroPy function ``real_repr``, you can see that it's made
up of the ``BinOp`` ``Add``, which adds the two numbers ``Num(1)`` and
``Num(2)``. Unparsing it into source code via ``unparse()`` gives you
``(1 + 2)``, which is what you would expect. In general, unparsing may
not give you exactly the original source, but it should be
semantically equivalent when executed. Take a look at the `data model
<#data-model>`_ to see what other useful conversions are available.

One (trivial) example of modifying the tree is to simply replace it
with a new tree, for example:

.. code:: python

  # macro_module.py
  from macropy.core.macros import Macros

  macros = Macros()

  @macros.expr
  def expand(tree, **kw):
      return Num(100)

When you run ``run.py``, this will print out ``100``, as the original
expression ``(1 + 2)`` has now been replaced by the literal
``100``. Another possible operation would be to replace the expression
with the square of itself:

.. code:: python

  # macro_module.py
  from macropy.core.macros import Macros

  macros = Macros()

  @macros.expr
  def expand(tree, **kw):
      newtree = BinOp(tree, Mult(), tree)
      return newtree


This will replace the expression ``(1 + 2)`` with ``((1 + 2) * (1 + 2))``;
you can similarly print out newtree via ``unparse`` or ``real_repr`` to
see what's it looks like.

Using Quasiquotes
~~~~~~~~~~~~~~~~~

Building up the new tree manually, as shown above, works reasonably
well. However, it can quickly get unwieldy, particularly for more
complex expressions. For example, let's say we wanted to make ``expand``
wrap the expression ``(1 + 2)`` in a lambda, like ``lambda x: x *
(1 + 2) + 10``. Ignore, for the moment, that this transform is not very
useful. Doing so manually is quite a pain:

.. code:: python

  # macro_module.py
  from macropy.core.macros import Macros

  macros = Macros()

  @macros.expr
  def expand(tree, **kw):
      return Lambda(arguments([Name("x", Param())], None, None, []), BinOp(BinOp(Name('x', Load()), Mult(), tree), Add(), Num(10)))


This works, and when you run ``run.py`` it prints out:

.. code:: python

  <function <lambda> at 0x00000000020A3588>


Because now ``target.py`` is printing out a lambda function. If we
modify ``target.py`` to call the expanded ``lambda`` with an argument:

.. code:: python

  # target.py
  from macro_module import macros, expand

  func = expand[1 + 2]
  print(func(5))


It prints ``25``, as you would expect.

`quasiquotes`:ref: are a special structure that lets you
quote sections of code as ASTs, letting us substitute in sections
dynamically. Quasiquotes let us turn the above code into:

.. code:: python

  # macro_module.py
  from macropy.core.macros import Macros
  from macropy.core.quotes import macros, q, ast_literal

  macros = Macros()

  @macros.expr
  def expand(tree, **kw):
      return q[lambda x: x * ast_literal[tree] + 10]


the ``q[...]`` syntax means that the section following it is quoted as
an AST, while the unquote ``ast_literal[...]`` syntax means to place
the *value* of ``tree`` into that part of the quoted AST, rather than
simply the node ``Name("tree")``. Running ``run.py``, this also prints
``25``. See [docs/examples/quasiquote <docs/examples/quasiquote>`_ for
the self-contained code for this example.

Another unquote ``u`` allow us to dynamically include the value ``10``
in the AST at run time:

.. code:: python

  # macro_module.py
  from macropy.core.macros import Macros
  from macropy.core.quotes import macros, q, ast_literal, u

  macros = Macros()

  @macros.expr
  def expand(tree, **kw):
      addition = 10
      return q[lambda x: x * ast_literal[tree] + u[addition]]


This will insert the a literal representing the value of ``addition``
into the position of the ``u[addition]``, in this case ``10``. This *also*
prints 25. For a more detailed description of how quoting and
unquoting works, and what more you can do with it, check out the
documentation for [Quaasiquotes <#quasiquotes>`_.

Apart from using the ``u`` and ``ast_literal`` unquotes to put things
into the AST, good old fashioned assignment works too:

.. code:: python

  # macro_module.py
  from macropy.core.macros import Macros
  from macropy.core.quotes import macros, q

  macros = Macros()

  @macros.expr
  def expand(tree, **kw):
      newtree = q[lambda x: x * None + 10]
      newtree.body.left.right = tree          # replace the None in the AST with the given tree
      return newtree


If you run this, it will also print ``25``.

Walking the AST
~~~~~~~~~~~~~~~

Quasiquotes make it much easier for you to manipulate sections of
code, allowing you to quickly put together snippets that look however
you want. However, they do not provide any support for a very common
use case: that of recursively traversing the AST and replacing
sections of it at a time.

Now that you know how to make basic macros, I will walk you through
the implementation of a less trivial (and extremely useful!) macro:
`quicklambda`:ref:.

If we look at what `quicklambda`:ref: does, we see want to take code
which looks like this:

.. code:: python

  f[_ + (1 * _)]


and turn it into:

.. code:: python

  (arg0 + (1 * arg1))


and wrap it in a lambda to give:

.. code:: python

  lambda arg0, arg1: (arg0 + (1 * arg1))


Let's accomplish the first transform first: we need to replace all the
``_`` with variables ``arg0``, ``arg1``, etc.. To do this, we need to
recurse over the AST in order to search for the uses of ``_``. A simple
attempt may be:

.. code:: python

  # macro_module.py

  from macropy.core.macros import Macros

  macros = Macros()

  @macros.expr
  def f(tree, **kw):
      names = ('arg' + str(i) for i in range(100))

      def rec(tree):
          if type(tree) is Name and tree.id == '_':
              tree.id = names.next()
          if type(tree) is BinOp:
              rec(tree.left)
              rec(tree.right)
          if type(tree) is List:
              map(rec, tree.elts)
          if type(tree) is UnaryOp:
              rec(tree.operand)
          if type(tree) is BoolOp:
              map(rec, tree.values)
          ...

      newtree = rec(tree)
      return newtree


Note that we use ``f`` instead of ``expand``. Also note that writing out
the recursion manually is pretty tricky, there are a ton of cases to
consider, and it's easy to get wrong. It turns out that this behavior,
of walking over the AST and doing something to it, is an extremely
common operation, common enough that MacroPy provides the ``Walker``
class to do this for you:

.. code:: python

  # macro_module.py
  from macropy.core.macros import Macros

  macros = Macros()

  @macros.expr
  def f(tree, **kw):
      names = ('arg' + str(i) for i in range(100))

      @Walker
      def underscore_search(tree, **kw):
          if type(tree) is Name and tree.id == '_':
              tree.id = names.next()

      newtree = underscore_search.recurse(tree)
      print(unparse(newtree)) # (arg0 + (1 * arg1))
      return newtree


This snippet of code is equivalent to the one earlier, except that
with a `walker`:ref:, you only need to specify the AST nodes you are
interested in (in this case ``Name``) and the Walker will do the
recursion automatically. As you can see, when we print out the
unparsed newtree, we can see that the transformed code looks like what
we expect. You could also use the `show_expanded`:ref: macro in
``target.py`` to see what it looks like:

.. code:: python

  # target.py
  from macro_module import macros, f
  from macropy.tracing import macros, show_expanded

  with show_expanded:
      my_func = f[_ + (1 * _)]
  # my_func = (arg0 + (1 * arg1))


Verifying that the code indeed is what we expect.

When run, this code then fails with a::

  NameError: name 'arg0' is not defined

At runtime, because the names we put into the tree (``arg0`` and ``arg1``)
haven't actually been defined in ``target.py``! We will see how we can
fix that.

More Walking
~~~~~~~~~~~~

The function being passed to the Walker can return a variety of
things. In this case, let's say we want to collect the names we
extracted from the ``names`` generator, so we can use them to populate
the arguments of the ``lambda``.

The Walker function request the ``collect`` argument, and call
``collect(item)`` to have the ``Walker`` aggregate them all in one large
list which you can extract by using ``recurse_collect`` instead of
``recurse``:

.. code:: python

  from macropy.core.macros import Macros
  from macropy.core.quotes import macros, q, u

  macros = Macros()

  @macros.expr
  def f(tree, **kw):
      names = ('arg' + str(i) for i in range(100))

      @Walker
      def underscore_search(tree, collect, **kw):
          if isinstance(tree, Name) and tree.id == "_":
              name = names.next()
              tree.id = name
              collect(name)
              return tree

      new_tree, used_names = underscore_search.recurse_collect(tree)
      print(used_names) # ['arg0', 'arg1']
      return new_tree


Now we have available both the ``new_tree`` as well as a list of
``used_names``. When we print out ``used_names``, we see it is the names
that got substituted in place of the underscores within the AST. If
you're wondering what other useful things are hiding in the ``**kw``,
check out the section on `walker`:ref:.

This still fails at runtime, but now all we need now is to wrap
everything in a ``lambda``, set the arguments properly:

.. code:: python

  from macropy.core.macros import Macros
  from macropy.core.quotes import macros, q, u, ast_literal

  _ = None  # makes IDE happy

  macros = Macros()

  @macros.expr
  def f(tree, **kw):
      names = ('arg' + str(i) for i in range(100))

      @Walker
      def underscore_search(tree, **kw):
          if isinstance(tree, Name) and tree.id == "_":
              name = names.next()
              tree.id = name
              return tree, collect(name)

      tree, used_names = underscore_search.recurse_collect(tree)

      new_tree = q[lambda: ast_literal[tree]]
      new_tree.args.args = [Name(id = x) for x in used_names]
      print(unparse(new_tree)) # (lambda arg0, arg1: (arg0 + (1 * arg1)))
      return new_tree


And we're done! The printed ``new_tree`` looks exactly like what we
want. The original code:

.. code:: python

  # target.py
  from macro_module import macros, f

  print(f[_ + (1 * _)])


spits out::

  <function <lambda> at 0x000000000203D198>

Showing we have successfully replaced all the underscores with
variables and wrapped the expression in a lambda! Now when we try to
run it:

.. code:: python

  # target.py
  from macro_module import macros, f

  my_func = f[_ + (1 * _)]
  print(my_func(10, 20)) # 30


It works! We can also use it in some less trivial cases, just to
verify that it indeed does what we want:

.. code:: python

  # target.py
  print(reduce(f[_ + _], [1, 2, 3]))  # 6
  print(filter(f[_ % 2 != 0], [1, 2, 3]))  # [1, 3]
  print(map(f[_  * 10], [1, 2, 3]))  # [10, 20, 30]


Mission Accomplished! You can see the completed self-contained example
in `docs/examples/full <docs/examples/full>`_. This macro is also
defined in our library in `macropy/quick_lambda.py
<macropy/quick_lambda.py>`_, along with a suite of `unit tests`__. It
is also used throughout the implementation of the other macros.

__ macropy/test/quick_lambda.py
