# -*- coding: utf-8 -*-
"""The main source of all things MacroPy"""

import ast
import functools
import importlib
import logging

from . import real_repr, walkers


logger = logging.getLogger(__name__)


class WrappedFunction(object):
    """Wraps a function which is meant to be handled (and removed) by
    macro expansion, and never called directly with square
    brackets.
    """
    def __init__(self, func, msg):
        self.func = func
        self.msg = msg
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        # print('Wrapped Function', dis.dis(self.func.__code__))
        return self.func(*args, **kwargs)

    def __getitem__(self, i):
        raise TypeError(self.msg.replace("%s", self.func.__name__))


def macro_function(func):
    """Wraps a function, to provide nicer error-messages in the common
    case where the macro is imported but macro-expansion isn't triggered."""
    return WrappedFunction(
        func,
        "Macro `%s` illegally invoked at runtime; did you import it "
        "properly using `from ... import macros, %s`?"
    )


def macro_stub(func):
    """Wraps a function that is a stub meant to be used by macros but
    never called directly.
    """

    return WrappedFunction(
        func,
        "Stub `%s` illegally invoked at runtime; is it used "
        "properly within a macro?"
    )


class Macros(object):
    """A registry of macros belonging to a module; used via

    .. code:: python
      macros = Macros()

      @macros.expr
      def my_macro(tree):
          ...

    Where the decorators are used to register functions as macros
    belonging to that module.
    """

    class Registry(object):

        def __init__(self, wrap = lambda x: x):
            self.registry = {}
            self.wrap = wrap

        def __call__(self, f, name=None):
            if name is not None:
                self.registry[name] = self.wrap(f)
            if hasattr(f, "__name__"):
                self.registry[f.__name__] = self.wrap(f)

            return self.wrap(f)

    def __init__(self):
        # Different kinds of macros
        self.expr = Macros.Registry(macro_function)
        self.block = Macros.Registry(macro_function)
        self.decorator = Macros.Registry(macro_function)

        self.expose_unhygienic = Macros.Registry()


# For other modules to hook into MacroPy's workflow while
# keeping this module itself unaware of their presence.
injected_vars = []      # functions to inject values throughout each
                        # files macros
filters = []            # functions to call on every macro-expanded snippet
post_processing = []    # functions to call on every macro-expanded file

def expand_entire_ast(tree, src, bindings):

    def expand_macros(tree):
        """Go through an AST, hunting for macro invocations and expanding any
        that are found.
        """

        def expand_if_in_registry(macro_tree, body_tree, args, registry,
                                  **kwargs):
            """Check if `tree` is a macro in `registry`, and if so use it to
            expand `args`."""

            # print(registry, file=sys.stderr)
            if isinstance(macro_tree, ast.Name) and macro_tree.id in registry:

                (the_macro, the_module) = registry[macro_tree.id]
                # print('Macro, module: %s, %s' % \
                #       (the_macro.func.__doc__, the_module), file=sys.stderr)
                # print('expand if in registry', body_tree, args, src,
                #       expand_macros, kwargs, file_vars, sep='\n',
                #       file=sys.stderr)
                try:
                    new_tree = the_macro(
                        tree=body_tree,
                        args=args,
                        src=src,
                        expand_macros=expand_macros,
                        **dict(list(kwargs.items()) + list(file_vars.items()))
                    )
                except Exception as e:
                    # here this exception is raised during macro
                    # expansion, at import time. If we come here, it
                    # means that the macro expanded to "raise
                    # Exception()" or something like that. This will
                    # be fixed in the failure filter, see failure.py
                    new_tree = e

                # print('Pre filters: %s' % new_tree, file=sys.stderr)

                for function in reversed(filters):
                    new_tree = function(
                        tree=new_tree,
                        args=args,
                        src=src,
                        expand_macros=expand_macros,
                        lineno=macro_tree.lineno,
                        col_offset=macro_tree.col_offset,
                        **dict(list(kwargs.items()) + list(file_vars.items()))
                    )
                return new_tree
            elif isinstance(macro_tree, ast.Call):
                args.extend(macro_tree.args)
                return expand_if_in_registry(macro_tree.func, body_tree, args,
                                             registry)

        def preserve_line_numbers(func):
            """Decorates a tree-transformer function to stick the original line
            numbers onto the transformed tree.
            """
            def run(tree):
                pos = ((tree.lineno, tree.col_offset)
                       if (hasattr(tree, "lineno") and
                           hasattr(tree, "col_offset"))
                       else None)
                new_tree = func(tree)

                if pos:
                    t = new_tree
                    while type(t) is list:
                        t = t[0]
                    (t.lineno, t.col_offset) = pos
                return new_tree
            return run

        @preserve_line_numbers
        def macro_expand(tree):
            """Tail Recursively expands all macros in a single AST node."""
            if isinstance(tree, ast.With):
                assert isinstance(tree.body, list), real_repr(tree.body)
                new_tree = tree.body
                for withitem in tree.items:
                    # TODO: this manages only one with block level??
                    new_tree = expand_if_in_registry(
                        withitem.context_expr,
                        new_tree,
                        [],
                        block_registry,
                        target=withitem.optional_vars)

                if new_tree:
                    if isinstance(new_tree, ast.expr):
                        new_tree = [ast.Expr(new_tree)]
                    if isinstance(new_tree, Exception): raise new_tree
                    assert isinstance(new_tree, list), type(new_tree)
                    return macro_expand(new_tree)

            # this detects a possible macro with syntax mname[...]
            if isinstance(tree, ast.Subscript) and type(tree.slice) is ast.Index:

                new_tree = expand_if_in_registry(tree.value, tree.slice.value,
                                                 [], expr_registry)

                if new_tree:
                    assert isinstance(new_tree, ast.expr), type(new_tree)
                    return macro_expand(new_tree)

            if isinstance(tree, (ast.AsyncFunctionDef, ast.ClassDef,
                                 ast.FunctionDef)):
                seen_decs = []
                additions = []
                while tree.decorator_list != []:
                    dec = tree.decorator_list[0]
                    tree.decorator_list = tree.decorator_list[1:]

                    new_tree = expand_if_in_registry(dec, tree, [],
                                                     decorator_registry)

                    if new_tree is None:
                        seen_decs.append(dec)
                    else:
                        tree = new_tree
                        tree = macro_expand(tree)
                        if type(tree) is list:
                            additions = tree[1:]
                            tree = tree[0]
                        elif isinstance(tree, ast.expr):
                            tree = [ast.Expr(tree)]
                            break

                if isinstance(tree, (ast.AsyncFunctionDef, ast.ClassDef,
                                     ast.FunctionDef)):
                    tree.decorator_list = seen_decs
                if len(additions) == 0:
                    return tree
                else:
                    return [tree] + additions

            return tree

        @walkers.Walker
        def macro_searcher(tree, **kw):
            x = macro_expand(tree)
            return x

        tree = macro_searcher.recurse(tree)

        return tree

    file_vars = {}

    for v in injected_vars:
        file_vars[v.__name__] = v(tree=tree, src=src,
                                  expand_macros=expand_macros, **file_vars)

    allnames = [
        (m, name, asname)
        for m, names in bindings
        for name, asname in names
    ]

    def extract_macros(pick_registry):
        return {
            asname: (registry[name], ma)
            for ma, name, asname in allnames
            for registry in [pick_registry(ma.macros).registry]
            if name in registry.keys()
        }

    block_registry = extract_macros(lambda x: x.block)
    expr_registry = extract_macros(lambda x: x.expr)
    decorator_registry = extract_macros(lambda x: x.decorator)

    # This is kind of a crude modification to handle from __future__
    # imports, simply removing them (and maybe a docstring) from the
    # front of the ast.Module.body list and sticking them back on
    # after all the macro processing.  It assumes that all trees at
    # this point are ast.Modules.  It might be better to make the
    # macro processors themselves ignore docstrings and __future__
    # imports.  For that matter, I don't know if macro processing
    # currently moves docstrings, either.
    preamble = None
    if isinstance(tree, ast.Module) and tree.body:
        if (isinstance(tree.body[0], ast.ImportFrom) and
            tree.body[0].module == '__future__'):
            preamble = [tree.body.pop(0)]
        elif (len(tree.body) > 1 and isinstance(tree.body[0], ast.Expr) and
              isinstance(tree.body[1], ast.ImportFrom) and
              tree.body[1].module == '__future__'):
            preamble = tree.body[0:1]
            del tree.body[0:1]

    tree = expand_macros(tree)

    for post in post_processing:
        tree = post(
            tree=tree,
            src=src,
            expand_macros=expand_macros,
            **file_vars
        )

    if preamble:
        tree.body = preamble + tree.body

    return tree


def detect_macros(tree, from_fullname, from_package=None, from_module=None):
    """Look for macros imports within an AST, transforming them and extracting
    the list of macro modules."""
    bindings = []

    logger.info("Finding macros in %r", from_fullname)
    for stmt in tree.body:
        # if the name is something like "from foo.bar import macros"
        if (isinstance(stmt, ast.ImportFrom) and
            stmt.module and stmt.names[0].name == 'macros' and
            stmt.names[0].asname is None):
            fullname = importlib.util.resolve_name(
                '.' * stmt.level + stmt.module, from_package)

            if fullname == __name__:
                continue

            logger.info("Importing macros from %r into %r", fullname,
                        from_module)
            mod = importlib.import_module(fullname)

            bindings.append((
                fullname,
                [(t.name, t.asname or t.name) for t in stmt.names[1:]]
            ))

            stmt.names = [
                name for name in stmt.names
                if name.name not in mod.macros.block.registry
                if name.name not in mod.macros.expr.registry
                if name.name not in mod.macros.decorator.registry
            ]

            stmt.names.extend([
                ast.alias(x, x) for x in
                mod.macros.expose_unhygienic.registry.keys()
            ])

    return bindings


def check_annotated(tree):
    """Shorthand for checking if an AST is of the form something[...]."""
    if (isinstance(tree, ast.Subscript) and type(tree.slice) is ast.Index and
        type(tree.value) is ast.Name):
        return tree.value.id, tree.slice.value
