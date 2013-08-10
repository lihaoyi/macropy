"""The main source of all things MacroPy"""

import sys
import imp
import ast
import itertools
from six import PY3
from ast import *
from .util import *
from .walkers import *


# TODO: How do we do this in py3?
if not PY3:
    # Monkey Patching pickle to pickle module objects properly
    import pickle
    pickle.Pickler.dispatch[type(pickle)] = pickle.Pickler.save_global


class WrappedFunction(object):
    """Wraps a function which is meant to be handled (and removed) by macro
    expansion, and never called directly with square brackets."""

    def __init__(self, func, msg):
        self.func = func
        self.msg = msg
        import functools
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __getitem__(self, i):
        raise TypeError(self.msg.replace("%s", self.func.__name__))


def macro_function(func):
    """Wraps a function, to provide nicer error-messages in the common
    case where the macro is imported but macro-expansion isn't triggered"""
    return WrappedFunction(
        func,
        "Macro `%s` illegally invoked at runtime; did you import it "
        "properly using `from ... import macros, %s`?"
    )


def macro_stub(func):
    """Wraps a function that is a stub meant to be used by macros but never
    called directly."""
    return WrappedFunction(
        func,
        "Stub `%s` illegally invoked at runtime; is it used "
        "properly within a macro?"
    )


class Macros(object):
    """A registry of macros belonging to a module; used via

    ```python
    macros = Macros()

    @macros.expr
    def my_macro(tree):
        ...
    ```

    Where the decorators are used to register functions as macros belonging
    to that module.
    """

    class Registry(object):
        def __init__(self, wrap = lambda x: x):
            self.registry = {}
            self.wrap = wrap

        def __call__(self, f, name=None):

            if name is not None:
                self.registry[name] = self.wrap(f)
            #if hasattr(f, "func_name"):
            #    self.registry[f.func_name] = self.wrap(f)
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
injected_vars = []      # functions to inject values throughout each files macros
filters = []            # functions to call on every macro-expanded snippet
post_processing = []    # functions to call on every macro-expanded file

def expand_entire_ast(tree, src, bindings):
    def expand_macros(tree):
        """Go through an AST, hunting for macro invocations and expanding any that
        are found"""

        def expand_if_in_registry(macro_tree, body_tree, args, registry, **kwargs):
            """check if `tree` is a macro in `registry`, and if so use it to expand `args`"""
            if isinstance(macro_tree, Name) and macro_tree.id in registry:

                (the_macro, the_module) = registry[macro_tree.id]
                try:
                    new_tree = the_macro(
                        tree=body_tree,
                        args=args,
                        src=src,
                        expand_macros=expand_macros,
                        **dict(list(kwargs.items()) + list(file_vars.items()))
                    )
                except Exception as e:
                    new_tree = e

                for filter in reversed(filters):
                    new_tree = filter(
                        tree=new_tree,
                        args=args,
                        src=src,
                        expand_macros=expand_macros,
                        lineno=macro_tree.lineno,
                        col_offset=macro_tree.col_offset,
                        **dict(list(kwargs.items()) + list(file_vars.items()))
                    )

                return new_tree
            elif isinstance(macro_tree, Call):
                args.extend(macro_tree.args)
                return expand_if_in_registry(macro_tree.func, body_tree, args, registry)

        def preserve_line_numbers(func):
            """Decorates a tree-transformer function to stick the original line
            numbers onto the transformed tree"""
            def run(tree):
                pos = (tree.lineno, tree.col_offset) if hasattr(tree, "lineno") and hasattr(tree, "col_offset") else None
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
            """Tail Recursively expands all macros in a single AST node"""
            #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            if isinstance(tree, With):
                assert isinstance(tree.body, list), real_repr(tree.body)
                if PY3:
                    new_tree = tree.body
                    for withitem in tree.items:
                        new_tree = expand_if_in_registry(
                                        withitem.context_expr, 
                                        new_tree, 
                                        [], 
                                        block_registry, 
                                        target=withitem.optional_vars)
                else:
                    new_tree = expand_if_in_registry(
                                        tree.context_expr, 
                                        tree.body, 
                                        [], 
                                        block_registry, 
                                        target=tree.optional_vars)
                



                if new_tree:
                    if isinstance(new_tree, expr):
                        new_tree = [Expr(new_tree)]
                    if isinstance(new_tree, Exception): raise new_tree
                    assert isinstance(new_tree, list), type(new_tree)
                    return macro_expand(new_tree)

            if isinstance(tree, Subscript) and type(tree.slice) is Index:

                new_tree = expand_if_in_registry(tree.value, tree.slice.value, [], expr_registry)

                if new_tree:
                    assert isinstance(new_tree, expr), type(new_tree)
                    return macro_expand(new_tree)

            if isinstance(tree, ClassDef) or isinstance(tree, FunctionDef):
                seen_decs = []
                additions = []
                while tree.decorator_list != []:
                    dec = tree.decorator_list[0]
                    tree.decorator_list = tree.decorator_list[1:]

                    new_tree = expand_if_in_registry(dec, tree, [], decorator_registry)

                    if new_tree is None:
                        seen_decs.append(dec)
                    else:
                        tree = new_tree
                        tree = macro_expand(tree)
                        if type(tree) is list:
                            additions = tree[1:]
                            tree = tree[0]
                        elif isinstance(tree, expr):
                            tree = [Expr(tree)]
                            break
                if type(tree) is ClassDef or type(tree) is FunctionDef:
                    tree.decorator_list = seen_decs
                if len(additions) == 0:
                    return tree
                else:
                    return [tree] + additions

            return tree

        @Walker
        def macro_searcher(tree, **kw):
            x = macro_expand(tree)
            return x

        tree = macro_searcher.recurse(tree)

        return tree


    file_vars = {}


    for v in injected_vars:
        file_vars[v.__name__] = v(tree=tree, src=src, expand_macros=expand_macros, **file_vars)


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

    tree = expand_macros(tree)

    for post in post_processing:
        tree = post(
            tree=tree,
            src=src,
            expand_macros=expand_macros,
            **file_vars
        )

    return tree


def detect_macros(tree):
    """Look for macros imports within an AST, transforming them and extracting
    the list of macro modules."""
    bindings = []

    for stmt in tree.body:
        if isinstance(stmt, ImportFrom) \
                and stmt.module \
                and stmt.names[0].name == 'macros' \
                and stmt.names[0].asname is None:
            __import__(stmt.module)
            mod = sys.modules[stmt.module]

            bindings.append((
                stmt.module,
                [(t.name, t.asname or t.name) for t in stmt.names[1:]]
            ))

            stmt.names = [
                name for name in stmt.names
                if name.name not in mod.macros.block.registry
                if name.name not in mod.macros.expr.registry
                if name.name not in mod.macros.decorator.registry
            ]

            stmt.names.extend([
                alias(x, x) for x in
                mod.macros.expose_unhygienic.registry.keys()
            ])

    return bindings

def check_annotated(tree):
    """Shorthand for checking if an AST is of the form something[...]"""
    if isinstance(tree, Subscript) and \
                    type(tree.slice) is Index and \
                    type(tree.value) is Name:
        return tree.value.id, tree.slice.value

