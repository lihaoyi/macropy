.. _exporting:
.. _exported:

Exporting your Expanded Code
----------------------------

Although MacroPy is designed to work seamlessly on-line, seamlessly
translating your code on the fly as it gets imported, without having
to trouble the programmer with a multi-stage expansion/execution
process. However, there are use reasons for performing an explicit
expansion:

- **performance**: walking the AST takes time, which may grow
  unbearable as the amount of code grows large. Pre-compiling (or at
  least caching) the macro-expanded code would save some frustration;

- **deployment**: you may be deploying your code in a Python
  environment where MacroPy doesn't function (e.g. Jython), or you may
  want to package your code as a library without forcing your users to
  have a dependency on MacroPy;

- **debugging**: although MacroPy provides tools to help figure out
  what's happening when things go wrong (e.g. `show_expanded`:ref:) it may
  sometimes to easier just to take a compile source dump of the entire
  source-tree after macro expansion so you can debug it directly,
  rather than through the expansion process.

MacroPy allows you to hook into the macro-expansion process via the
``macropy.exporter`` variable, which comes with three bundled values
which can satisfy these constraints:

- `NullExporter()`_: this is the default exporter,
  which does nothing;

- `SaveExporter(target, root)`_: this saves
  a copy of your code tree (rooted at ``root``), with macros expanded,
  in the ``target`` directory. This is a convenient way of exporting the
  entire source tree with macros expanded;

- `PycExporter()`_: this emulates the normal ``.pyc``
  compilation and caching based on file ``mtime``. This is a convenient
  transparent-ish cache to avoid needlessly performing macro-expansion
  repeatedly.

NullExporter()
~~~~~~~~~~~~~~

This is the default Exporter, and although it does not do anything, it
illustrates the general contract of what an Exporter must look like:

.. code:: python

  class NullExporter(object):
      def find(self, file, pathname, description, module_name, package_path):
          pass

      def export_transformed(self, code, tree, module_name, file_name):
          pass


In short, it has two methods: ``find`` and ``export_transformed``:

- ``find`` is called after a file has been loaded and the use of
  macros have been detected inside. It can either return ``None``, in
  which case macro-expansion goes ahead, or a ``module`` object, in
  which case macro-expansion is simply skipped and the returned
  ``module`` object is used instead;

- ``export_transformed`` is called after macro-expansion has been
  successfully completed (It is not triggered on failures). Whatever
  it returns doesn't matter.

The arguments to these methods are relatively self explanatory, but
feel free to inject ``print`` statements into ``NullExporter`` if you
want to see what's what.

SaveExporter(target, root)
~~~~~~~~~~~~~~~~~~~~~~~~~~

This exporter is activated immediately after the initial ``import
macropy.activate`` statement, via:

.. code:: python

  import macropy.activate
  macropy.exporter = SaveExporter("exported", ".")


It creates a copy of your source tree (rooted at ``root``) in the
``target`` directory, and any file which is macro-expanded will have its
expanded representation saved in that directory. For example, if you
have a project::

  run.py
  my_macro.py
  file.py
  stuff/
      thing.py


Assuming ``run.py`` is the entry point containing the ``import
macropy.activate`` statement, we need to:

- modify it, as shown above, to contain the ``macropy.exporter =
  SaveExporter(..., ...)`` line;
- run it, via ``python run.py`` or similar.

::

  run.py
  my_macro.py
  file.py
  stuff/
      thing.py
  saved/
      run.py
      my_macro.py
      file.py
      stuff/
          thing.py


Where all macros within the files in the ``saved/`` subdirectory which
were executed in the course of execution have been expanded. You can
verify this by removing the ``import macropy.activate`` and
``macropy.exporter = ...`` lines from ``saved/run.py`` (Thereby disabling
MacroPy) and executing ``saved/run.py`` directly. Everything should run
as normal, demonstrating that all macros have been expanded the
dependencies on MacroPy's import hooks and AST transformations have
been removed.

Note that *only macros in files which get expanded in the execution of
the program will have their expanded versions saved*. This allows you
to control which files you want to perform the
macro-expansion-and-save on: for example, most projects have utility
scripts which cannot be imported from the root, or example files which
are similarly not directly importable.

In most cases, activating the ``SaveExporter`` and executing your test
suite should cause all files necessary to be imported, expanded and
saved. If you need more customization, you could easily create a
script that performs exactly the imports you need, or `imports all
modules in a folder`__, or any other behavior your want.

__ http://stackoverflow.com/questions/1057431/loading-all-modules-in-a-folder-in-python

Pre-expanding the MacroPy Test Suite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following example can be used to expand-and-save MacroPy's own
test suite, such that it can be run without macros:

.. code:: python

  # run_tests.py
  import unittest
  import macropy.activate
  from macropy.core.exporters import SaveExporter
  macropy.exporter = SaveExporter("exported", ".")
  import macropy.test

  unittest.TextTestRunner().run(macropy.test.Tests)


MacroPy's test suite clearly makes *extremely extensive* use of
macros. Nevertheless, activating ``SaveExporter`` before running the
test suite makes a copy of the entire source-tree with all macros
expanded; inspecting any of the previously-macro-using files in the
newly-created ``exported/`` directory demonstrates that the macros have
really, truly, been expanded:

.. code:: python

  # exported/macropy/string_interp.py
  from pickle import loads as sym1
  import re
  from macropy.core.macros import Macros
  from macropy.core.hquotes import macros, u, ast_list
  macros = Macros()

  @macros.expr
  def s(tree, **kw):
      captured = []
      new_string = ''
      chunks = re.split('{(.*?)}', tree.s)
      for i in range(0, len(chunks)):
          if ((i % 2) == 0):
              new_string += chunks[i]
          else:
              new_string += '%s'
              captured += [chunks[i]]
      result = BinOp(left=ast_repr(new_string), op=Mod(), right=Call(func=Captured(tuple, 'tuple'), args=[List(elts=map(parse_expr, captured))], keywords=[], starargs=None, kwargs=None))
      return result


We can disable MacroPy's runtime transformations completely by
removing the import hook:

.. code:: python

  # exported/macropy/__init__.py
  import sys
  import core.import_hooks
  import core.exporters
  import os
  # sys.meta_path.append(core.import_hooks.MacroFinder)
  __version__ = "0.2.0"
  exporter = core.exporters.NullExporter()


And when we run the saved, macro-expanded, macro-less version via ``cd
exported; python run_tests.py``::

  ----------------------------------------------------------------------
  Ran 76 tests in 0.150s

  FAILED (failures=4, errors=1)


A few minor failures, mainly in the error-message/line-numbers tests,
as the pre-expanded code will have different line numbers than the
just-in-time-expanded ASTs. Nonetheless, on the whole it works.

------------------------------------------------

The SaveExporter should be of great help to any library-author who
wants to use Macros internally (e.g. `case_classes`:ref: to simplify class
declarations, or `peg`:ref: to write a parser) but does not want to
saddle users of the library with having to activate import hooks, or
wants to run the code in an environment where such functionality is
not supported (e.g. Jython).

By using the ``SaveExporter``, the macro-using code is expanded into
plain Python, and although it may rely on MacroPy as a library
(e.g. the ``CaseClass`` class in `macropy/experimental/peg.py`:repo:)
it won't need any of MacroPy's import-code-intercepting
AST-transforming capabilities at run-time.

PycExporter()
~~~~~~~~~~~~~

.. warning::

  Due to changes in the way compiled source files are stored,
  PycExporter is not yet functional in MacroPy3.

The PycExporter makes MacroPy perform the same ``*.pc -> *.pyc`` caching
that the normal Python import process does. This can be activated via:

.. code:: python

  import macropy.activate
  macropy.exporter = PycExporter()


The macro-expansion process takes significantly longer than normal
imports, and this may be helpful if you have a large number of large
files using macros and you want to save having to re-expand them every
execution.

Although ``PycExporter`` automatically does the recompilation of the
macro-expanded files when they are modified, it notably *does not* do
recompilation of the macro-expanded files when *the macros* are
modified. This means that ``PycExporter`` is not useful when doing
development on the macros themselves, since the output files will not
get properly recompiled when the macros change. For now it is best to
simply use the `NullExporter()`_ when messing with your
macros, and only using the `PycExporter()`_ when your
macros are stable and you are working on the target code.
