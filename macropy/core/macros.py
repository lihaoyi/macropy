import sys
import imp
import ast
import itertools
from ast import *
from util import *
from walkers import *
from misc import *
import weakref

class MacroFunction(object):
    def __init__(self, func):
        self.func = func
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
    def __getitem__(self, i):
        raise TypeError(
            "Macro `%s` illegally invoked at runtime; did you import it "
            "properly using `from ... import macros, %s`?" % ((self.func.func_name,) * 2)
        )
class Macros(object):
    """A registry of macros belonging to a module; used via

    ```python
    macros = Macros()

    @macros.expr()
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

        def __call__(self):
            def register(f, name=None):
                if name is not None:
                    self.registry[name] = self.wrap(f)
                if hasattr(f, "func_name"):
                    self.registry[f.func_name] = self.wrap(f)
                if hasattr(f, "__name__"):
                    self.registry[f.__name__] = self.wrap(f)

                return self.wrap(f)
            return register

    def __init__(self):

        # Different kinds of macros
        self.expr = Macros.Registry(MacroFunction)
        self.block = Macros.Registry(MacroFunction)
        self.decorator = Macros.Registry(MacroFunction)


        self.expose_unhygienic = Macros.Registry()

        self.registered = []
    def register(self, thing):
        self.registered.append(thing)

        return len(self.registered)-1

class _MacroLoader(object):
    """Performs the loading of a module with macro expansion."""
    def __init__(self, module_name, tree, source, file_name, bindings, module_aliases):
        self.module_name = module_name
        self.tree = tree
        self.source = source
        self.file_name = file_name
        self.bindings = bindings
        self.module_aliases = module_aliases

    def load_module(self, fullname):

        for (p, _) in self.bindings:
            __import__(p)

        modules = [(sys.modules[p], bindings) for (p, bindings) in self.bindings]

        tree = expand_ast(self.tree, self.source, modules, self.module_aliases)

        ispkg = False
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = []
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        mod.__file__ = self.file_name

        try:
            exec compile(tree, self.file_name, "exec") in mod.__dict__
        except Exception as e:
            import traceback
            traceback.print_exc()

        return mod



def expand_ast(tree, src, bindings, module_aliases):
    """Go through an AST, hunting for macro invocations and expanding any that
    are found"""

    # you don't pay for what you don't use
    positions = Lazy(lambda: indexer.recurse_real(tree)[1])
    line_lengths = Lazy(lambda: map(len, src.split("\n")))
    indexes = Lazy(lambda: distinct([linear_index(line_lengths(), l, c) for (l, c) in positions()] + [len(src)]))
    symbols = Lazy(lambda: _gen_syms(tree))


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


    def expand_if_in_registry(tree, body, args, registry, **kwargs):
        """check if `tree` is a macro in `registry`, and if so use it to expand `args`"""
        if isinstance(tree, Name) and tree.id in registry:

            (the_macro, the_module) = registry[tree.id]
            new_tree = the_macro(
                tree=body,
                args=args,
                gen_sym=lambda: symbols().next(),

                exact_src=lambda t: src_for(t, src, indexes, line_lengths),
                expand_macros=lambda t: expand_ast(t, src, bindings, module_aliases),
                module_alias=module_aliases[the_module],
                **kwargs
            )

            new_tree = ast_ctx_fixer.recurse(new_tree, Load())
            fill_line_numbers(new_tree, tree.lineno, tree.col_offset)
            return new_tree
        elif isinstance(tree, Call):
            args.extend(tree.args)
            return expand_if_in_registry(tree.func, body, args, registry)

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



@singleton
class MacroFinder(object):
    """Loads a module and looks for macros inside, only providing a loader if
    it finds some."""
    def find_module(self, module_name, package_path):
        try:
            (file, pathname, description) = imp.find_module(
                module_name.split('.')[-1],
                package_path
            )
            txt = file.read()

            # short circuit heuristic to fail fast if the source code can't
            # possible contain the macro import at all
            if " import macros" not in txt:
                return

            # check properly the AST if the macro import really exists
            tree = ast.parse(txt)

            bindings, module_aliases = detect_macros(tree)

            if bindings == []:
                return # no macros found, carry on
            else:
                return _MacroLoader(module_name, tree, txt, file.name, bindings,  module_aliases)
        except Exception, e:
            pass

def _gen_syms(tree):
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

    tree, found_names = name_finder.recurse_real(tree)
    names = ("sym" + str(i) for i in itertools.count())
    return itertools.ifilter(lambda x: x not in found_names, names)

def detect_macros(tree):
    """Look for macros imports within an AST, transforming them and extracting
    the list of macro modules."""
    bindings = []


    module_aliases = {}
    symbols = Lazy(lambda: _gen_syms(tree))
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

            module_aliases[mod] = symbols().next()
            stmt.names.extend(
                [alias(x, x) for x in
                 mod.macros.expose_unhygienic.registry.keys()]
            )
    try:
        tree.body = [
            Import([alias(mod.__name__, name)], lineno = 1, col_offset = 0)
            for (mod, name) in module_aliases.items()
        ] + tree.body
    except Exception, e:
        import traceback
        traceback.print_exc()
        raise e

    return bindings, module_aliases

def check_annotated(tree):
    if isinstance(tree, Subscript) and \
                    type(tree.slice) is Index and \
                    type(tree.value) is Name:
        return tree.value.id, tree.slice.value