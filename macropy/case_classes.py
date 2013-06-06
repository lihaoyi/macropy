from macropy.core.macros import *
from macropy.core.quotes import macros, q, u

__all__ = []

macros = Macros()

@macros.expose()
def apply(f):
    return f()

@macros.expose()
class CaseClass(object):
    __slots__ = []

    def copy(self, **kwargs):
        old = map(lambda a: (a, getattr(self, a)), self._fields)
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


def extract_args(init_fun, bases):
    args = []
    vararg = None
    kwarg = None
    defaults = []
    for base in bases:
        if type(base) is Name:
            args.append(base.id)
        if type(base) is List:
            vararg = base.elts[0].id

        if type(base) is Set:
            kwarg = base.elts[0].id
        if type(base) is BinOp and type(base.op) is BitOr:
            args.append(base.left.id)
            defaults.append(base.right)

    all_args = args[:]
    if vararg:
        all_args.append(vararg)
    if kwarg:

        all_args.append(kwarg)
    return args, vararg, kwarg, defaults, all_args

@Walker
def find_member_assignments(tree, collect, stop, **kw):
    if type(tree) in [GeneratorExp, Lambda, ListComp, DictComp, SetComp, FunctionDef, ClassDef]:
        stop()
    if type(tree) is Assign:
        self_assigns = [
            t.attr for t in tree.targets
            if type(t) is Attribute
            and type(t.value) is Name
            and t.value.id == "self"
        ]
        map(collect, self_assigns)

@macros.decorator()
def case(tree, gen_sym, hygienic_names, **kw):
    def split_body(tree):
        new_body = []
        outer = []
        init_body = []
        for statement in tree.body:
            if type(statement) is ClassDef:
                outer.append(_case_transform(statement, [tree.name]))
                with q as a:
                    name[tree.name].b = name[statement.name]
                a_old = a[0]
                a_old.targets[0].attr = statement.name

                a_new = parse_stmt(unparse_ast(a[0]))[0]
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
            with q as a:
                self.x = name[x]

            a[0].targets[0].attr = x

            init_fun.body.append(a[0])

    def _case_transform(tree, parents):

        with q as methods:
            def __init__(self, *args, **kwargs):
                pass

            _fields = []
            _varargs = None
            _kwargs = None
            __slots__ = []

        init_fun, set_fields, set_varargs, set_kwargs, set_slots, = methods

        args, vararg, kwarg, defaults, all_args = extract_args(init_fun, tree.bases)

        if vararg:
            set_varargs.value = Str(vararg)
        if kwarg:
            set_kwargs.value = Str(kwarg)

        additional_members = find_member_assignments.recurse_real(tree.body)[1]

        prep_initialization(init_fun, args, vararg, kwarg, defaults, all_args)
        set_fields.value.elts = map(Str, args)
        set_slots.value.elts = map(Str, all_args + additional_members)

        new_body, outer, init_body = split_body(tree)
        init_fun.body.extend(init_body)
        with q as assign:
            @apply
            def x():
                pass

        assign[0].name = gen_sym()
        assign[0].body += outer

        tree.body = new_body
        tree.bases = [Name(id=x, ctx=Load()) for x in parents]

        tree.body = methods + tree.body

        return [tree] + (assign if len(outer) > 0 else [])

    x = _case_transform(tree, [hygienic_names("CaseClass")])
    return x