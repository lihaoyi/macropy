"""Macro providing an extremely concise way of declaring classes"""

import ast

from .core import parse_stmt, unparse, ast_repr  # noqa: F401
from .core.macros import Macros
from .core.walkers import Walker
from .core.hquotes import macros, hq, unhygienic, u
from .core.quotes import ast_literal, name
from .core.analysis import Scoped


macros = Macros()  # noqa: F811


def apply(f):
    return f()


class CaseClass(object):

    __slots__ = []

    def copy(self, **kwargs):
        old = list(map(lambda a: (a, getattr(self, a)), self._fields))
        new = list(kwargs.items())
        return self.__class__(**dict(old + new))

    def __str__(self):
        return (self.__class__.__name__ + "(" +
                ", ".join(str(getattr(self, x))
                          for x in self.__class__._fields) + ")")

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        try:
            return self.__class__ == other.__class__ \
                and all(getattr(self, x) == getattr(other, x)
                        for x in self.__class__._fields)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        for x in self.__class__._fields:
            yield getattr(self, x)


class Enum(object):

    def __new__(cls, *args, **kw):
        if not hasattr(cls, "all"):
            cls.all = []
        thing = super(Enum, cls).__new__(cls)
        cls.all.append(thing)
        return thing

    @property
    def next(self):
        return self.__class__.all[(self.id + 1) % len(self.__class__.all)]
    @property
    def prev(self):
        return self.__class__.all[(self.id - 1) % len(self.__class__.all)]

    def __str__(self):
        return self.__class__.__name__ + "." + self.name

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        for x in self.__class__._fields:
            yield getattr(self, x)


def enum_new(cls, **kw):
    if len(kw) != 1:
        raise TypeError("Enum selection can only take exactly 1 named "
                        "argument: %d found." % len(kw))

    [(k, v)] = kw.items()

    for value in cls.all:
        if getattr(value, k) == v:
            return value

    raise ValueError("No Enum found for %s=%s" % (k, v))


def noop_init(*args, **kw):
    pass


def extract_args(bases):
    args = []
    vararg = None
    kwarg = None
    defaults = []
    for base in bases:
        if type(base) is ast.Name:
            args.append(base.id)

        elif type(base) is ast.List:
            vararg = base.elts[0].id

        elif type(base) is ast.Set:
            kwarg = base.elts[0].id

        elif type(base) is ast.BinOp and type(base.op) is ast.BitOr:
            args.append(base.left.id)
            defaults.append(base.right)
        else:
            assert False, ("Illegal expression in case class signature: " +
                           unparse(base))

    all_args = args[:]
    if vararg:
        all_args.append(vararg)
    if kwarg:
        all_args.append(kwarg)
    return args, vararg, kwarg, defaults, all_args


def find_members(tree, name):
    @Scoped
    @Walker
    def find_member_assignments(tree, collect, stop, scope, **kw):
        if name in scope.keys():
            stop()
        elif type(tree) is ast.Assign:
            self_assigns = [
                t.attr for t in tree.targets
                if type(t) is ast.Attribute
                and type(t.value) is ast.Name
                and t.value.id == name
            ]
            for assign in self_assigns:
                collect(assign)
    return find_member_assignments.collect(tree)


def split_body(tree, gen_sym):
        new_body = []
        outer = []
        init_body = []
        for statement in tree.body:
            if type(statement) is ast.ClassDef:
                outer.append(case_transform(statement, gen_sym,
                                            [ast.Name(id=tree.name)]))
                with hq as a:
                    name[tree.name].b = name[statement.name]
                a_old = a[0]
                a_old.targets[0].attr = statement.name

                a_new = parse_stmt(unparse(a[0]))[0]
                outer.append(a_new)
            elif type(statement) is ast.FunctionDef:
                new_body.append(statement)
            else:
                init_body.append(statement)
        return new_body, outer, init_body


def prep_initialization(init_fun, args, vararg, kwarg, defaults, all_args):

    kws = {'vararg': vararg, 'kwarg': kwarg, 'defaults': defaults}
    kws.update({
        'kwonlyargs': [],
        'kw_defaults': [],
        'args': [ast.arg('self', None)] + [ast.arg(id, None) for id
                                           in args],
        'vararg': ast.arg(vararg, None) if vararg is not None else None,
        'kwarg': ast.arg(kwarg, None) if kwarg is not None else None,
    })

    init_fun.args = ast.arguments(**kws)

    for x in all_args:
        with hq as a:
            unhygienic[self.x] = name[x]  # noqa: F821

        a[0].targets[0].attr = x

        init_fun.body.append(a[0])


def shared_transform(tree, gen_sym, additional_args=[]):
    with hq as methods:
        def __init__(self, *args, **kwargs):
            pass

        _fields = []  # noqa: F841
        _varargs = None  # noqa: F841
        _kwargs = None  # noqa: F841
        __slots__ = []  # noqa: F841

    init_fun, set_fields, set_varargs, set_kwargs, set_slots, = methods

    args, vararg, kwarg, defaults, all_args = extract_args(
        [ast.Name(id=x) for x in additional_args] + tree.bases
    )

    if vararg:
        set_varargs.value = ast.Str(vararg)

    if kwarg:
        set_kwargs.value = ast.Str(kwarg)

    nested = [
        n for f in tree.body
        if type(f) is ast.FunctionDef
        if len(f.args.args) > 0
        for n in find_members(f.body, f.args.args[0].arg)
    ]

    additional_members = find_members(tree.body, "self") + nested

    prep_initialization(init_fun, args, vararg, kwarg, defaults, all_args)
    set_fields.value.elts = list(map(ast.Str, args))
    set_slots.value.elts = list(map(ast.Str, all_args + additional_members))
    new_body, outer, init_body = split_body(tree, gen_sym)
    init_fun.body.extend(init_body)
    tree.body = new_body
    tree.body = methods + tree.body

    return outer


def case_transform(tree, gen_sym, parents):
    outer = shared_transform(tree, gen_sym)
    tree.bases = parents
    assign = ast.FunctionDef(
        gen_sym("prepare_"+tree.name),
        ast.arguments([], None, [], [], None, []),
        outer,
        [hq[apply]],
        None
    )
    return [tree] + ([assign] if len(outer) > 0 else [])


@macros.decorator
def case(tree, gen_sym, **kw):
    """Macro providing an extremely concise way of declaring classes"""
    x = case_transform(tree, gen_sym, [hq[CaseClass]])

    return x


@macros.decorator
def enum(tree, gen_sym, exact_src, **kw):

    count = [0]
    new_assigns = []
    new_body = []

    def handle(expr):
        assert type(expr) in (ast.Name, ast.Call), ast.stmt.value
        if type(expr) is ast.Name:
            expr.ctx = ast.Store()
            self_ref = ast.Attribute(value=ast.Name(id=tree.name), attr=expr.id)
            with hq as code:
                ast_literal[self_ref] = name[tree.name](u[count[0]], u[expr.id])
            new_assigns.extend(code)
            count[0] += 1

        elif type(expr) is ast.Call:
            assert type(expr.func) is ast.Name
            self_ref = ast.Attribute(value=ast.Name(id=tree.name),
                                     attr=expr.func.id)
            id = expr.func.id
            expr.func = ast.Name(id=tree.name)

            expr.args = [ast.Num(count[0]), ast.Str(id)] + expr.args
            new_assigns.append(ast.Assign([self_ref], expr))
            count[0] += 1

    for stmt in tree.body:
        try:
            if type(stmt) is ast.Expr:
                assert type(stmt.value) in (ast.Tuple, ast.Name, ast.Call)
                if type(stmt.value) is ast.Tuple:
                    for el in stmt.value.elts:
                        handle(el)
                else:
                    handle(stmt.value)
            elif type(stmt) is ast.FunctionDef:
                new_body.append(stmt)
            else:
                assert False

        except AssertionError as e:
            assert False, ("Can't have `%s` in body of enum" %
                           unparse(stmt).strip("\n"))

    tree.body = new_body + [ast.Pass()]

    shared_transform(tree, gen_sym, additional_args=["id", "name"])

    with hq as code:
        name[tree.name].__new__ = staticmethod(enum_new)
        name[tree.name].__init__ = noop_init

    tree.bases = [hq[Enum]]

    return [tree] + new_assigns + code
