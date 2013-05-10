from macropy.core.macros import *
from macropy.core.lift import macros, q, name, ast


def replace(tree):
    print "replace", tree
    if type(tree) is list:
        all_lets = []
        new_tree = []
        for thing in tree:
            l, t = replace(thing)
            all_lets.append(l)
            new_tree.append(t)
        return all_lets, new_tree

    if type(tree) in [Lambda, GeneratorExp, ListComp, SetComp, DictComp]:
        return [], tree
    if type(tree) is Call and type(tree.func) is Lambda:
        all_lets = walk_children(tree.func.body)
        return [tree] + all_lets, tree.func.body
    if isinstance(tree, AST):
        walk_children(tree)


    return [], tree

def walk_children(tree):
    all_lets = []
    for field, old_value in list(iter_fields(tree)):
        old_value = getattr(tree, field, None)
        lets, new_value = replace(old_value)
        all_lets.append(lets)
        setattr(tree, field, new_value)
    return all_lets
tree = q%(lambda x: x + (lambda y: y + 1)(3))(5)
goal = q%(lambda x: (lambda y: (x + (y + 1)))(3))(5)

print unparse_ast(tree)
lets, new_tree = replace(tree)
print flatten(lets)
print unparse_ast(new_tree)