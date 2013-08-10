"""Macro providing an extremely concise way of declaring classes"""
from macropy.core.macros import *
from macropy.core.hquotes import macros, hq, name, unhygienic, u
from macropy.core.analysis import Scoped
macros = Macros()

def apply(f):
    return f()


class CaseClass(object):
    __slots__ = []

    def copy(self, **kwargs):
        old = list(map(lambda a: (a, getattr(self, a)), self._fields))
        new = kwargs.items()
        return self.__class__(**dict(old + new))

    def __str__(self):
        return self.__class__.__name__ + "(" + ", ".join(str(getattr(self, x)) for x in self.__class__._fields) + ")"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        try:
            return self.__class__ == other.__class__ \
                and all(getattr(self, x) == getattr(other, x) for x in self.__class__._fields)
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
        thing = object.__new__(cls, *args, **kw)
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
        raise TypeError("Enum selection can only take exactly 1 named argument: " + len(kw) + " found.")

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
        if type(base) is Name:
            args.append(base.id)

        elif type(base) is List:
            vararg = base.elts[0].id

        elif type(base) is Set:
            kwarg = base.elts[0].id

        elif type(base) is BinOp and type(base.op) is BitOr:
            args.append(base.left.id)
            defaults.append(base.right)
        else:
            assert False, "Illegal expression in case class signature: " + unparse(base)

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
        elif type(tree) is Assign:
            self_assigns = [
                t.attr for t in tree.targets
                if type(t) is Attribute
                and type(t.value) is Name
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
            if type(statement) is ClassDef:
                outer.append(case_transform(statement, gen_sym, [Name(id=tree.name)]))
                with hq as a:
                    name[tree.name].b = name[statement.name]
                a_old = a[0]
                a_old.targets[0].attr = statement.name

                a_new = parse_stmt(unparse(a[0]))[0]
                outer.append(a_new)
            elif type(statement) is FunctionDef:
                new_body.append(statement)
            else:
                init_body.append(statement)
        return new_body, outer, init_body


def prep_initialization(init_fun, args, vararg, kwarg, defaults, all_args):

    init_fun.args = arguments(
        args = [Name(id="self")] + [Name(id = id) for id in args],
        vararg = vararg,
        kwarg = kwarg,
        defaults = defaults
    )

    for x in all_args:
        with hq as a:
            unhygienic[self.x] = name[x]

        a[0].targets[0].attr = x

        init_fun.body.append(a[0])


def shared_transform(tree, gen_sym, additional_args=[]):
    with hq as methods:
        def __init__(self, *args, **kwargs):
            pass

        _fields = []
        _varargs = None
        _kwargs = None
        __slots__ = []

    init_fun, set_fields, set_varargs, set_kwargs, set_slots, = methods

    args, vararg, kwarg, defaults, all_args = extract_args(
        [Name(id=x) for x in additional_args] + tree.bases
    )

    if vararg:
        set_varargs.value = Str(vararg)

    if kwarg:
        set_kwargs.value = Str(kwarg)

    nested = [
        n
        for f in tree.body
        if type(f) is FunctionDef
        if len(f.args.args) > 0
        for n in find_members(f.body, f.args.args[0].id)
    ]

    additional_members = find_members(tree.body, "self") + nested

    prep_initialization(init_fun, args, vararg, kwarg, defaults, all_args)
    set_fields.value.elts = list(map(Str, args))
    set_slots.value.elts = list(map(Str, all_args + additional_members))
    new_body, outer, init_body = split_body(tree, gen_sym)
    init_fun.body.extend(init_body)
    tree.body = new_body
    tree.body = methods + tree.body

    return outer


def case_transform(tree, gen_sym, parents):

    outer = shared_transform(tree, gen_sym)

    tree.bases = parents
    assign = FunctionDef(
        gen_sym("prepare_"+tree.name),
        arguments([], None, None, []),
        outer,
        [hq[apply]]
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
        assert type(expr) in (Name, Call), stmt.value
        if type(expr) is Name:
            expr.ctx = Store()
            self_ref = Attribute(value=Name(id=tree.name), attr=expr.id)
            with hq as code:
                ast[self_ref] = name[tree.name](u[count[0]], u[expr.id])
            new_assigns.extend(code)
            count[0] += 1

        elif type(expr) is Call:
            assert type(expr.func) is Name
            self_ref = Attribute(value=Name(id=tree.name), attr=expr.func.id)
            id = expr.func.id
            expr.func = Name(id=tree.name)

            expr.args = [Num(count[0]), Str(id)] + expr.args
            new_assigns.append(Assign([self_ref], expr))
            count[0] += 1

    for stmt in tree.body:
        try:
            if type(stmt) is Expr:
                assert type(stmt.value) in (Tuple, Name, Call)
                if type(stmt.value) is Tuple:
                    for el in stmt.value.elts: 
                        handle(el)
                else:
                    handle(stmt.value)
            elif type(stmt) is FunctionDef:
                new_body.append(stmt)
            else:
                assert False

        except AssertionError as e:
            assert False, "Can't have `%s` in body of enum" % unparse(stmt).strip("\n")

    tree.body = new_body + [Pass()]

    shared_transform(tree, gen_sym, additional_args=["id", "name"])

    with hq as code:
        name[tree.name].__new__ = staticmethod(enum_new)
        name[tree.name].__init__ = noop_init


    tree.bases = [hq[Enum]]

    return [tree] + new_assigns + code