import sys
import imp
import ast
import itertools
from ast import *
from util import *
from walkers import *


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
    def __init__(self):
        self.expr_registry = {}
        self.decorator_registry = {}
        self.block_registry = {}

    def expr(self, inside_out=False):
        def register(f):
            self.expr_registry[f.func_name] = (f, inside_out)
            return f
        return register

    def decorator(self, inside_out=False):
        def register(f):
            self.decorator_registry[f.func_name] = (f, inside_out)
            return f
        return register

    def block(self, inside_out=False):
        def register(f):
            self.block_registry[f.func_name] = (f, inside_out)
            return f
        return register


def fill_line_numbers(tree, lineno, col_offset):
    """Fill in line numbers somewhat more cleverly than the
    ast.fix_missing_locations method, which doesn't take into account the
    fact that line numbers are monotonically increasing down lists of AST
    nodes."""
    if type(tree) is list:
        for sub in tree:
            if isinstance(sub, AST) \
                    and hasattr(sub, "lineno") \
                    and hasattr(sub, "col_offset") \
                    and (sub.lineno, sub.col_offset) > (lineno, col_offset):

                lineno = sub.lineno
                col_offset = sub.col_offset

            fill_line_numbers(sub, lineno, col_offset)
    elif isinstance(tree, AST):
        if not (hasattr(tree, "lineno") and hasattr(tree, "col_offset")):
            tree.lineno = lineno
            tree.col_offset = col_offset
        for name, sub in ast.iter_fields(tree):
            fill_line_numbers(sub, tree.lineno, tree.col_offset)

@Walker
def _ast_ctx_fixer(tree, ctx, **kw):
    """Fix any missing `ctx` attributes within an AST; allows you to build
    your ASTs without caring about that stuff and just filling it in later."""
    if "ctx" in type(tree)._fields and not hasattr(tree, "ctx"):
        tree.ctx = ctx

    if type(tree) is arguments:
        for arg in tree.args:
            _ast_ctx_fixer.recurse(arg, Param())
        for default in tree.defaults:
            _ast_ctx_fixer.recurse(default, Load())

        return tree, stop

    if type(tree) is AugAssign:
        _ast_ctx_fixer.recurse(tree.target, AugStore())
        _ast_ctx_fixer.recurse(tree.value, AugLoad())
        return tree, stop

    if type(tree) is Assign:
        for target in tree.targets:
            _ast_ctx_fixer.recurse(target, Store())

        _ast_ctx_fixer.recurse(tree.value, Load())
        return tree, stop

    if type(tree) is Delete:
        for target in tree.targets:
            _ast_ctx_fixer.recurse(target, Del())
        return tree, stop

class _MacroLoader(object):
    """Performs the loading of a module with macro expansion."""
    def __init__(self, module_name, tree, source, file_name, required_pkgs):
        self.module_name = module_name
        self.tree = tree
        self.source = source
        self.file_name = file_name
        self.required_pkgs = required_pkgs

    def load_module(self, fullname):

        for p in self.required_pkgs:
            __import__(p)

        modules = [sys.modules[p] for p in self.required_pkgs]

        tree = process_ast(self.tree, self.source, modules)
        ispkg = False
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = []
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        exec compile(tree, self.file_name, "exec") in mod.__dict__
        return mod

def process_ast(tree, src, modules):
    """Takes an AST and spits out an AST, doing macro expansion in additon to
    some post-processing"""
    tree = _expand_ast(tree, src, modules)

    tree = _ast_ctx_fixer.recurse(tree, Load())

    fill_line_numbers(tree, 0, 0)
    return tree

def detect_macros(tree):
    """Look for macros imports within an AST, transforming them and extracting
    the list of macro modules."""
    required_pkgs = []
    for stmt in tree.body:
        if isinstance(stmt, ImportFrom) \
                and stmt.names[0].name == 'macros' \
                and stmt.names[0].asname is  None:
            required_pkgs.append(stmt.module)
            stmt.names = [alias(name='*', asname=None)]
    return required_pkgs


def linear_index(line_lengths, lineno, col_offset):
    prev_length = sum(line_lengths[:lineno-1]) + lineno-2
    out = prev_length + col_offset + 1
    return out

@Walker
def indexer(tree, **kw):
    try:

        unparse_ast(tree)

        return collect((tree.lineno, tree.col_offset))
    except Exception, e:
        pass

def _src_for(tree, src, indexes, line_lengths):

        all_child_pos = sorted(indexer.recurse_real(tree)[1])
        start_index = linear_index(line_lengths, *all_child_pos[0])

        last_child_index = linear_index(line_lengths, *all_child_pos[-1])

        first_successor_index = indexes[min(indexes.index(last_child_index)+1, len(indexes)-1)]


        for end_index in range(last_child_index, first_successor_index):
            transforms = {
                GeneratorExp: "(%s)",
                ListComp: "[%s]",
                SetComp: "{%s}",
                DictComp: "{%s}"
            }

            prelim = src[start_index:end_index]
            prelim = transforms.get(type(tree), "%s") % prelim
            if isinstance(tree, stmt):
                prelim = prelim.replace("\n" + " " * tree.col_offset, "\n")

            try:
                parsed = ast.parse(prelim)
                if unparse_ast(parsed).strip() == unparse_ast(tree).strip():
                    return src[start_index:end_index].replace("\n" + " " * tree.col_offset, "\n")

            except SyntaxError as e:
                pass
        raise Exception("Can't find working source")


def _expand_ast(tree, src, modules):
    """Go through an AST, hunting for macro invocations and expanding any that
    are found"""
    def merge_dicts(my_dict):
        return dict((k,v) for d in my_dict for (k,v) in d.items())

    positions = indexer.recurse_real(tree)[1]
    line_lengths = map(len, src.split("\n"))
    indexes = [linear_index(line_lengths, l, c) for (l, c) in positions] + [len(src)]

    block_registry     = merge_dicts(m.macros.block_registry for m in modules)
    expr_registry      = merge_dicts(m.macros.expr_registry for m in modules)
    decorator_registry = merge_dicts(m.macros.decorator_registry for m in modules)

    symbols = gen_syms(tree)

    def expand_if_in_registry(tree, body, args, registry, **kwargs):
        """check if `tree` is a macro in `registry`, and if so use it to expand `args`"""
        if isinstance(tree, Name) and tree.id in registry:
            the_macro, inside_out = registry[tree.id]
            return the_macro(
                tree=body,
                args=args,
                gen_sym=lambda: symbols.next(),
                src_for=lambda t: _src_for(t, src, indexes, line_lengths),
                **kwargs
            )
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
                if type(new_tree) is list:
                    new_tree = flatten(new_tree)
                    (new_tree[0].lineno, new_tree[0].col_offset) = pos
                else:
                    (new_tree.lineno, new_tree.col_offset) = pos
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

        if isinstance(tree, BinOp) and type(tree.op) is Mod:
            new_tree = expand_if_in_registry(tree.left, tree.right, [], expr_registry)

            if new_tree:
                assert isinstance(new_tree, expr), type(new_tree)
                return macro_expand(new_tree)

        if isinstance(tree, ClassDef) or isinstance(tree, FunctionDef):
            all_decs = tree.decorator_list[:]
            seen_decs = []
            while tree.decorator_list != []:
                dec = tree.decorator_list[0]
                tree.decorator_list = tree.decorator_list[1:]

                new_tree = expand_if_in_registry(dec, tree, [], decorator_registry)
                if new_tree is None:

                    seen_decs.append(dec)
                else:
                    tree = new_tree
                    tree = macro_expand(tree)

            tree.decorator_list = seen_decs
            return tree

        return tree


    @Walker
    def macro_searcher(tree, **kw):
        return macro_expand(tree)

    tree = macro_searcher.recurse(tree)

    return tree


@sys.meta_path.append
@singleton
class _MacroFinder(object):
    """Loads a module and looks for macros inside, only providing a loader if
    it finds some."""
    def find_module(self, module_name, package_path):
        try:
            (file, pathname, description) = imp.find_module(
                module_name.split('.')[-1],
                package_path
            )
            txt = file.read()
            tree = ast.parse(txt)
            required_pkgs = detect_macros(tree)
            if required_pkgs == []:
                return # no macros found, carry on
            else:
                return _MacroLoader(module_name, tree, txt, file.name, required_pkgs)
        except Exception, e:
            pass

def gen_syms(tree):
    """Create a generator that creates symbols which are not used in the given
    `tree`. This means they will be hygienic, i.e. it guarantees that they will
    not cause accidental shadowing, as long as the scope of the new symbol is
    limited to `tree` e.g. by a lambda expression or a function body"""
    @Walker
    def name_finder(tree, **kw):
        if type(tree) is Name:
            return collect(tree.id)

    tree, found_names = name_finder.recurse_real(tree)
    names = ("sym" + str(i) for i in itertools.count())
    return itertools.ifilter(lambda x: x not in found_names, names)

