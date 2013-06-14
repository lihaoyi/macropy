"""The main source of all things MacroPy"""

import sys
import imp
import ast
import itertools
from ast import *
from util import *
from walkers import *
from misc import *


@singleton
class hygienic_self_ref:
    pass


class MacroFunction(object):
    """Wraps a macro-function, to provide nicer error-messages in the common
    case where the macro is imported but macro-expansion isn't triggered"""
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __getitem__(self, i):
        raise TypeError(
            "Macro `%s` illegally invoked at runtime; did you import it "
            "properly using `from ... import macros, %s`?"
            % (self.func.func_name, self.func.func_name)
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
            if hasattr(f, "func_name"):
                self.registry[f.func_name] = self.wrap(f)
            if hasattr(f, "__name__"):
                self.registry[f.__name__] = self.wrap(f)

            return self.wrap(f)

    def __init__(self):
        # Different kinds of macros
        self.expr = Macros.Registry(MacroFunction)
        self.block = Macros.Registry(MacroFunction)
        self.decorator = Macros.Registry(MacroFunction)

        self.expose_unhygienic = Macros.Registry()


def fill_hygienes(tree, captured_registry, gen_sym):
    @Walker
    def hygienator(tree, stop, **kw):
        if type(tree) is Captured:
            new_sym = [sym for val, sym in captured_registry if val is tree.val]
            if not new_sym:
                new_sym = gen_sym()

                captured_registry.append((tree.val, new_sym))
            else:
                new_sym = new_sym[0]
            return Name(new_sym, Load())


    return hygienator.recurse(tree)


def expand_entire_ast(tree, src, bindings):
    symbols = Lazy(lambda: gen_sym(tree))
    captured_registry = []
    registry_alias = symbols().next()

    # you don't pay for what you don't use
    positions = Lazy(lambda: indexer.collect(tree))
    line_lengths = Lazy(lambda: map(len, src.split("\n")))
    indexes = Lazy(lambda: distinct([linear_index(line_lengths(), l, c) for (l, c) in positions()] + [len(src)]))

    allnames = [(m, name, asname) for m, names in bindings for name, asname in names]

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

    def expand_ast(tree):
        """Go through an AST, hunting for macro invocations and expanding any that
        are found"""

        def expand_if_in_registry(macro_tree, body_tree, args, registry, **kwargs):
            """check if `tree` is a macro in `registry`, and if so use it to expand `args`"""
            if isinstance(macro_tree, Name) and macro_tree.id in registry:

                (the_macro, the_module) = registry[macro_tree.id]
                new_tree = the_macro(
                    tree=body_tree,
                    args=args,
                    gen_sym=lambda: symbols().next(),

                    exact_src=lambda t: exact_src(t, src, indexes, line_lengths),
                    expand_macros=lambda t: expand_ast(t),
                    **kwargs
                )
                fill_hygienes(new_tree, captured_registry, lambda: symbols().next())
                new_tree = ast_ctx_fixer.recurse(new_tree, Load())
                fill_line_numbers(new_tree, macro_tree.lineno, macro_tree.col_offset)
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
            if isinstance(tree, With):
                assert isinstance(tree.body, list), real_repr(tree.body)
                new_tree = expand_if_in_registry(tree.context_expr, tree.body, [], block_registry, target=tree.optional_vars)

                if new_tree:
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
    tree = expand_ast(tree)
    unpickle_name = symbols().next()
    pickle_import = [
        ImportFrom(module='pickle', names=[alias(name='loads', asname=unpickle_name)], level=0)
    ]
    try:
        import pickle
        stored = [
            Assign(
                [Tuple([Name(id=sym, ctx=Store()) for val, sym in captured_registry], Store())],
                Call(
                    Name(id=unpickle_name, ctx=Load()),
                    [Str(pickle.dumps([val for val, sym in captured_registry]))], [], None, None
                )
            )

        ] if captured_registry else []
        tree.body = map(fix_missing_locations, pickle_import + stored) + tree.body

    except Exception, e:
        import traceback
        traceback.print_exc()
        raise e
    return tree


def gen_sym(tree):
    """Create a generator that creates symbols which are not used in the given
    `tree`. This means they will be hygienic, i.e. it guarantees that they will
    not cause accidental shadowing, as long as the scope of the new symbol is
    limited to `tree` e.g. by a lambda expression or a function body"""
    @Walker
    def name_finder(tree, collect, **kw):
        if type(tree) is Name:
            collect(tree.id)
        if type(tree) is Import:
            names = [x.asname or x.name for x in tree.names]
            map(collect, names)
        if type(tree) is ImportFrom:
            names = [x.asname or x.name for x in tree.names]
            map(collect, names)

    found_names = name_finder.collect(tree)
    names = ("sym" + str(i) for i in itertools.count())
    return itertools.ifilter(lambda x: x not in found_names, names)


def detect_macros(tree):
    """Look for macros imports within an AST, transforming them and extracting
    the list of macro modules."""
    bindings = []


    for stmt in tree.body:
        if isinstance(stmt, ImportFrom) \
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


