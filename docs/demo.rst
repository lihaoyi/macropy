.. _demo:

Demo Macros
===========

Below are a few example uses of macros that are implemented (together
with test cases!) in the `macropy <macropy>`:repo: and
`macropy/experimental <macropy/experimental>`:repo: folders. These are
also the ideal places to go look at to learn to write your own macros:
check out the source code of the `String Interpolation
<macropy/string_interp.py>`:repo: or `Quick Lambda
<macropy/quick_lambda.py>`:repo: macros for some small (<30 lines),
self contained examples. Their `unit
<macropy/test/string_interp.py>`:repo:` `tests
<macropy/test/quick_lambda.py>`:repo: demonstrate how these macros are
used.

Feel free to open up a REPL and try out the examples in the console;
simply ``import macropy.console``, and most of the examples should
work right off the bat when pasted in! Macros in this section are also
relatively stable and well-tested, and you can rely on them to work
and not to suddenly change from version to version.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   case_classes
   enums
   quick_lambda
   lazy
   interned
   interpolation
   tracing
   peg
