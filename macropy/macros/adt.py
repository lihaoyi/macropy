from macropy.core.core import *
from macropy.core.macros import *
from macropy.core.lift import macros, q, u

macros = True

NO_ARG = object()

def case_transform(tree, parents):

    def self_get(x):
        mini_tree = q%self.x
        mini_tree.attr = x
        return mini_tree


    var_names = [name.id for name in tree.bases]
    list_tree = List(elts = map(self_get, var_names))


    def compare_field(x):
        mini_tree = q%(self.x == other.x)
        mini_tree.left.attr = x
        mini_tree.comparators[0].attr = x
        return mini_tree

    eq_list_tree = List(elts = map(compare_field, var_names))

    with q as methods:
        def __init__(self):
            pass
        def __str__(self):
            return u%tree.name + "(" + ", ".join(map(str, ast%list_tree)) + ")"

        def __repr__(self):
            return self.__str__()

        def __eq__(self, other):
            try:
                return all(ast%eq_list_tree)
            except:
                return False

        def __ne__(self, other):
            return not self.__eq__(other)
        def copy(self):
            return Thing()

    init_fun, str_fun, repr_fun, eq_fun, ne_fun, copy_fun = methods

    copy_fun.args.args += [Name(id = n, ctx=Param()) for n in var_names]
    copy_fun.args.defaults = [q%NO_ARG for n in var_names]
    ret = copy_fun.body[0].value
    ret.func = Name(id=tree.name)


    ret.args = [q%(ast%self_get(n) if name%n is NO_ARG else name%n) for n in var_names]

    init_fun.args.args += tree.bases

    for name in tree.bases:
        with q as setter:
            self.x = x
        setter[0].targets[0].attr = name.id
        setter[0].value = name
        init_fun.body += setter

    init_fun.body += [
        statement for statement in tree.body
        if type(statement) is not FunctionDef
    ]

    new_body = []
    new_classes = []
    for statement in tree.body:
        if type(statement) is ClassDef:
            new_classes += [case_transform(statement, [Name(id = tree.name)])]
        elif type(statement) is FunctionDef:
            new_body += [statement]

    tree.body = new_body
    tree.bases = parents

    tree.decorator_list = []
    tree.body += methods
    out = [tree] + new_classes

    return out

@decorator_macro
def case(tree):
    return case_transform(tree, [q%object])