# -*- coding: utf-8 -*-
"""The main source of all things MacroPy"""

from abc import ABC, abstractmethod
import ast
import collections
import functools
import importlib
import inspect
import logging

from . import compat, real_repr, Captured, Literal


logger = logging.getLogger(__name__)


class WrappedFunction:
    """Wraps a function which is meant to be handled (and removed) by
    macro expansion, and never called directly with square
    brackets.
    """
    def __init__(self, func, msg):
        self.func = func
        self.msg = msg
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
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


MacroData = collections.namedtuple('MacroData', ['macro', 'macro_tree',
                                                 'body_tree', 'call_args',
                                                 'kwargs', 'name'])


class MacroType(ABC):
    """Base class for the macro types. Each macro type has a name that
    will be used as the name of its registry (lowered). Each type
    should implement `detect_macro`:meth:.

    :param registry: A `Macros.Registry`:class: instance
    """

    def __init__(self, registry):
        self.registry = registry

    def get_macro_details(self, macro_tree):
        if isinstance(macro_tree, ast.Call):
            call_args = tuple(macro_tree.args)
            macro_tree = macro_tree.func
        else:
            call_args = ()
        if isinstance(macro_tree, ast.Name):
            return macro_tree.id, macro_tree, call_args
        else:
            return None, macro_tree, call_args

    @abstractmethod
    def detect_macro(self, in_tree):
        """This is a coroutine (a synchronous one) that should test
        ``in_tree`` and find out if it's a macro "call". If that's the
        case. It will yield a `MacroData`:class: object containing the
        details of the macro. The calling logic will "send" in a tree
        corresponding with the ``MacroData.body_tree`` value but with
        the macros expanded. At that point the coroutine has the
        chance to yield the next macro found (if the definition allows
        that, like with *block* or *decorator* macros) and the process
        repeats. If no other macro is found the sent-in tree can be
        modified/checked before returning it with the normal ``return``
        statement.

        :param in_tree: an AST tree
        :returns: an AST tree or None
        """


class Expr(MacroType):
    """Handles macros of the expression type, defined by using square
    brackets, like ``amacro[foo]``."""

    def detect_macro(self, in_tree):
        if (isinstance(in_tree, ast.Subscript) and
            type(in_tree.slice) is ast.Index):  # noqa: E129
            body_tree = in_tree.slice.value
            name, macro_tree, call_args = self.get_macro_details(in_tree.value)
            if name is not None and name in self.registry:
                new_tree = yield MacroData(self.registry[name], macro_tree,
                                           body_tree, call_args, {}, name)
                assert isinstance(new_tree, ast.expr), ('Wrong type %r' %
                                                        type(new_tree))
                new_tree = ast.Expr(new_tree)


class Block(MacroType):
    """Handles block macros, defined by using a ``with`` statement, like:

    .. code:: python

      with amacro:
          do_something

    """

    def detect_macro(self, in_tree):
        if isinstance(in_tree, ast.With):
            assert isinstance(in_tree.body, list), real_repr(in_tree.body)
            new_tree = None
            for wi in in_tree.items:
                name, macro_tree, call_args = self.get_macro_details(
                    wi.context_expr)
                if name is not None and name in self.registry:
                    new_tree = yield MacroData(self.registry[name], macro_tree,
                                               in_tree.body, call_args,
                                               {'target': wi.optional_vars},
                                               name)

            if new_tree:
                if isinstance(new_tree, ast.expr):
                    new_tree = [ast.Expr(new_tree)]
                if isinstance(new_tree, Exception):
                    raise new_tree
                assert isinstance(new_tree, list), type(new_tree)
            return new_tree


class Decorator(MacroType):
    """Handles macros defined as decorators, like:

    .. code:: python

      @amacro
      @anothermacro
      def foo():
          ...

    The macros will be expanded with an inside-out order, thus
    executing ``anothermacro`` first and then ``amacro``.
    """

    def detect_macro(self, in_tree):
        if (isinstance(in_tree, compat.scope_nodes) and
            len(in_tree.decorator_list)):  # noqa: E129
            rev_decs = list(reversed(in_tree.decorator_list))
            in_tree.decorator_list = []
            tree = in_tree
            seen_decs = []
            additions = []
            # process each decorator from the innermost outwards
            for dec in rev_decs:
                name, macro_tree, call_args = self.get_macro_details(dec)
                # if the decorator is not a macro, add it to a list
                # for later re-insertion, either before executing an
                # outer macro or at the end of the loop if no macro is found
                if name is None or name not in self.registry:
                    seen_decs.append(dec)
                    continue
                # if the node is still a scope node, re-insert skipped
                # decorators together with those added by a previous cycle
                if isinstance(tree, compat.scope_nodes) and len(seen_decs):
                    tree.decorator_list = (list(reversed(seen_decs)) +
                                           tree.decorator_list)
                    seen_decs = []
                tree = yield MacroData(self.registry[name], macro_tree, tree,
                                       call_args, {}, name)
                if type(tree) is list:
                    additions = tree[1:]
                    tree = tree[0]
                elif isinstance(tree, ast.expr):
                    tree = [ast.Expr(tree)]
                    break
            else:
                # if the final tree is still a scope node (something
                # decorable), add the remaining decorators
                if isinstance(tree, compat.scope_nodes) and len(seen_decs):
                    tree.decorator_list = (list(reversed(seen_decs)) +
                                           tree.decorator_list)

            if len(additions) == 0:
                return tree
            else:
                return [tree] + additions


class Macros:
    """A registry of macros belonging to a module; used via

    .. code:: python
      macros = Macros()

      @macros.expr
      def my_macro(tree):
          ...

    Where the decorators are used to register functions as macros
    belonging to that module.
    """

    class Registry:
        """a map between names and functions defined as macros. To be used as
        decorator on the macro function, it takes a a wrapper function.

        :param wrap: A function that will be called with the
          registering macro function as parameter
        """

        def __init__(self, wrap=lambda x: x):
            self.registry = {}
            self.wrap = wrap

        def __call__(self, f, name=None):
            if name is not None:
                self.registry[name] = f
            else:
                if hasattr(f, "__name__"):
                    self.registry[f.__name__] = f
                else:
                    raise ValueError("You should specify a name")
            return self.wrap(f)

    """The types of macros that will be handled by the registry."""
    macro_types = (Expr, Block, Decorator)

    def __init__(self):
        # Different kinds of macros
        self.macro_registries = []
        for cls in self.macro_types:
            self.add_macro_type(cls, macro_function)

        self.expose_unhygienic = Macros.Registry()

    def add_macro_type(self, macrotype_cls, wrap_func):
        """For the given ``macrotype_cls``, creates a new
        `Macros.Registry`:class: and registers it with the type name
        (lowercased)."""
        assert issubclass(macrotype_cls, MacroType), "Invalid macro type class"
        reg = Macros.Registry(wrap_func)
        setattr(self, macrotype_cls.__name__.lower(), reg)
        self.macro_registries.append(reg.registry)


# For other modules to hook into MacroPy's workflow while
# keeping this module itself unaware of their presence.
"""Functions to inject values throughout each files macros."""
injected_vars = []
"""Functions to call on every macro-expanded snippet."""
filters = []
"""Functions to call on every macro-expanded file."""
post_processing = []


def preserve_line_numbers(tree, new_tree):
    """Decorates a tree-transformer function to stick the original line
    numbers onto the transformed tree.
    """
    pos = ((tree.lineno, tree.col_offset)
           if (hasattr(tree, "lineno") and
               hasattr(tree, "col_offset"))
           else None)
    if pos:
        t = new_tree
        while type(t) is list:
            t = t[0]
        (t.lineno, t.col_offset) = pos


class ExpansionContext:
    """Knows how to walk over AST nodes and some other utility classes and
    at each level tries to expand the macros, if present.

    Differenty from the previous implementation this allows for macros
    to be defined inside the body of other macros, where it's
    permitted by the syntax. This means that trees like:

    .. code:: python

      foo[bar[...]]

    or

    .. code:: python

      with foo:
          bar[...]
          ...

    (other combinations avoided for brevity)

    are now permitted. In such cases ``bar`` is expanded first and
    ``foo`` will be expanded after, not with the original *unexpanded*
    tree but with the version that contains the modifications made by
    ``bar``.

    :param tree: an AST tree
    :param parent: an optional `ExpansionContext`:class: instance to be used
      as parent

    """

    """An optional `ExtensionContext`:class: instance that will be used as
    source for the values of the other members, except ``tree``."""
    parent = None

    """A mapping containing the *realization* of the `~.injected_vars`,
    which are calculated per-module."""
    file_vars = {}

    """A list containing one or more instances of `MacroType`:class:
    subclasses, usually defined as per-module level."""
    macro_types = []

    def __init__(self, tree, parent=None):
        self.tree = tree
        if parent is not None:
            assert isinstance(parent, ExpansionContext)
            self.parent = parent
            self.file_vars = parent.file_vars
            self.macro_types = parent.macro_types

    def expand_macros(self, tree=None):
        """Basic expansion function, It just calls `~.walk_tree`:meth: with
        the ``tree`` passed in at instantiation time if it's not passed as
        parameter.

        :param tree: an AST tree
        :returns: an AST tree
        """
        if tree is None:
            tree = self.tree
        return self.walk_tree(tree)

    def macro_expand(self, tree):
        """This is a coroutine that expands found macros, and yields back
        transformed AST tree for the calling "walking" logic to transform.

        :param tree: an AST tree
        :returns: an AST tree or ``None``
        """
        new_tree = None
        found_macro = False
        # for every macro type
        for mtype in self.macro_types:
            new_tree = None
            # its ``detect_macro()`` is a coro, start a pull/send cycle
            type_it = mtype.detect_macro(tree)
            try:
                # each coro will yield a MacroData instance until
                # exhausted, in which case it will raise a
                # StopIteration with a possible final ``.value`` member
                while True:
                    mdata = type_it.send(new_tree)
                    logger.debug("Found macro %r, type %r, line %d",
                                 mdata.name, mtype.__class__.__name__,
                                 mdata.macro_tree.lineno)
                    found_macro = True
                    mfunc, mmod = mdata.macro
                    # if the macro function is itself a coro, give  it
                    # control about when expand its body, if before or
                    # after its own expansion, it's similar in spirit
                    # to ``contextlib.contexmanager()`` decorator
                    if inspect.isgeneratorfunction(mfunc):
                        new_tree = mdata.body_tree
                    else:
                        # if not yield it for a pre-execution walking
                        new_tree = yield mdata.body_tree
                    try:
                        new_tree = mfunc(
                            tree=new_tree,
                            args=mdata.call_args,
                            src=self.src,
                            expand_macros=self.expand_macros,
                            **dict(tuple(mdata.kwargs.items()) +
                                   tuple(self.file_vars.items()))
                        )
                        # the result is a generator, treat it like a
                        # context manager
                        if inspect.isgenerator(new_tree):
                            m_it = new_tree
                            new_tree = None
                            try:
                                while True:
                                    new_tree = yield m_it.send(new_tree)
                            except StopIteration as final:
                                if final.value is not None:
                                    new_tree = final.value
                    except Exception as e:
                        # here this exception is raised during macro
                        # expansion, at import time. If we come here,
                        # it means that the macro expanded to "raise
                        # Exception()" or something like that. This
                        # will be fixed in the failure filter, see
                        # failure.py
                        new_tree = e

                    # apply the filters
                    for function in reversed(filters):
                        new_tree = function(
                            tree=new_tree,
                            args=mdata.call_args,
                            src=self.src,
                            expand_macros=self.expand_macros,
                            lineno=mdata.macro_tree.lineno,
                            col_offset=mdata.macro_tree.col_offset,
                            **dict(tuple(mdata.kwargs.items()) +
                                   tuple(self.file_vars.items()))
                        )
                    # yield it for one more walking
                    new_tree = yield new_tree
            except StopIteration as final:
                # if the ``detect_macro()`` function returns a final
                # value, take it and ext as well, if it has found at
                # least one macro
                if final.value is not None:
                    new_tree = final.value
                if found_macro:
                    break
        return new_tree

    def walk_children(self, tree):
        """Walks each field of an AST instance or a list containing AST
        instances and calls ``~.walk_tree``:meth: on them.

        :param tree: an AST tree
        :returns: None
        """
        if isinstance(tree, ast.AST):
            for field, old_value in ast.iter_fields(tree):
                old_value = getattr(tree, field, None)
                new_value = self.walk_tree(old_value)
                setattr(tree, field, new_value)
        elif isinstance(tree, list) and len(tree) > 0:
            new_tree = []
            for t in tree:
                new_t = self.walk_tree(t)
                if type(new_t) is list:
                    new_tree.extend(new_t)
                else:
                    new_tree.append(new_t)
            tree[:] = new_tree

    def walk_tree(self, tree):
        """Calls `~.macro_expand`:meth: and walks each tree yielded by it,
        one time **before** the transformation and one time **after**
        it.

        :param tree: an AST tree
        :returns: an AST tree
        """
        if (isinstance(tree, ast.AST) or type(tree) is Literal or
            type(tree) is Captured):  # noqa: #E129
            expand_it = self.macro_expand(tree)
            new_tree = None
            try:
                while True:
                    new_tree = self.walk_tree(expand_it.send(new_tree))
            except StopIteration as final:
                # accept the return value from ``macro_expand`` only
                # if at least one macro was found
                if final.value is not None and new_tree is not None:
                    new_tree = self.walk_tree(final.value)
            if new_tree is not None:
                preserve_line_numbers(tree, new_tree)
                tree = new_tree
        self.walk_children(tree)
        return tree


class ModuleExpansionContext(ExpansionContext):
    """A subclass of the `ExpansionContext`:class: tailored to be
    instantiatiated per-module (directly by the import-level hooks, when
    they are active).

    :param tree: an AST tree
    :param src: the source string of the ``tree``
    :param bindings: a mapping between each imported macro module and its used
      macro names
    """

    def __init__(self, tree, src, bindings):
        super().__init__(tree)
        self.src = src
        self.file_vars = {}
        for v in injected_vars:
            self.file_vars[v.__name__] = v(tree=tree, src=src,
                                           expand_macros=self.expand_macros,
                                           **self.file_vars)

        allnames = [
            (mod, name, asname)
            for mod, names in bindings
            for name, asname in names
        ]

        self.macro_types = [cls({
            asname: (registry[name], mod)
            for mod, name, asname in allnames
            for registry in [mod.macros.macro_registries[ix]]
            if name in registry.keys()
        }) for ix, cls in enumerate(Macros.macro_types)]

    def expand_macros(self, tree=None):
        if tree is None:
            tree = self.tree
        else:
            return super().expand_macros(tree)

        preamble = self.pre_process(tree)
        tree = super().expand_macros(tree)
        tree = self.post_process(tree)

        if preamble:
            tree.body = preamble + tree.body

        return tree

    def pre_process(self, tree):
        """Removes ``from __future__`` imports from the tree's body and
        returns them.

        :param tree: an AST tree
        :returns: an AST tree or ``None``
        """
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
                tree.body[0].module == '__future__'):  # noqa: E129
                preamble = [tree.body.pop(0)]
            elif (len(tree.body) > 1 and isinstance(tree.body[0], ast.Expr) and
                  isinstance(tree.body[1], ast.ImportFrom) and
                  tree.body[1].module == '__future__'):
                preamble = tree.body[0:1]
                del tree.body[0:1]
        return preamble

    def post_process(self, tree):
        """Executes the functions added to the `~.post_processing` list.

        :param tree: an AST tree
        :returns: an AST tree
        """
        for post in post_processing:
            tree = post(
                tree=tree,
                src=self.src,
                expand_macros=self.expand_macros,
                **self.file_vars
            )
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
            stmt.names[0].asname is None):  # noqa: E129
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
        type(tree.value) is ast.Name):  # noqa: E129
        return tree.value.id, tree.slice.value
