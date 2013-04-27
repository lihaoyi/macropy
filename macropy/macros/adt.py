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
    list_tree = q%[]
    list_tree.elts = map(self_get, var_names)

    with q as str_fun:
        def __str__(self):
            return u%tree.name + "(" + ", ".join(map(str, u%list_tree)) + ")"

        def __repr__(self):
            return self.__str__()

    with q as init_fun:
        def __init__(self):
            pass

    def compare_field(x):
        mini_tree = q%(self.x == other.x)
        mini_tree.left.attr = x
        mini_tree.comparators[0].attr = x
        return mini_tree

    eq_list_tree = q%[]
    eq_list_tree.elts = map(compare_field, var_names)
    with q as eq_fun:
        def __eq__(self, other):
            try:
                return all(u%eq_list_tree)
            except:
                return False

    with q as copy_fun:
        def copy(self):
            return Thing()

    copy_fun[0].args.args += [Name(id = n, ctx=Param()) for n in var_names]
    copy_fun[0].args.defaults = [q%NO_ARG for n in var_names]
    ret = copy_fun[0].body[0].value
    ret.func = Name(id=tree.name)


    ret.args = [q%(u%self_get(n) if u%Name(id=n) is NO_ARG else u%Name(id=n)) for n in var_names]

    tree.body += eq_fun
    init_fun[0].args.args += tree.bases

    for name in tree.bases:
        with q as setter:
            self.x = x
        setter[0].targets[0].attr = name.id
        setter[0].value = name
        init_fun[0].body += setter

    new_body = []
    new_classes = []
    for statement in tree.body:
        if type(statement) is ClassDef:
            new_classes += [case_transform(statement, [Name(id = tree.name)])]
        else:
            new_body += [statement]

    tree.body = new_body
    tree.bases = parents

    tree.decorator_list = []
    tree.body += str_fun
    tree.body += init_fun
    tree.body += copy_fun
    out = [tree] + new_classes

    return out

@decorator_macro
def case(tree):
    return case_transform(tree, [])