from macropy.core.macros import *
from macropy.core.lift import macros, q, u

macros = Macros()

NO_ARG = object()

def link_children(cls):
    for child in cls._children:
        new_child = type(child.__name__, (cls, CaseClass), dict(**child.__dict__))
        setattr(cls, child.__name__, new_child)
    return cls

class CaseClass(object):
    def __init__(self, *args, **kwargs):
        for k, v in zip(self.__class__._fields, args) + kwargs.items():
            setattr(self, k, v)

    def copy(self, **kwargs):
        return self.__class__(**dict(self.__dict__.items() + kwargs.items()))

    def __str__(self):
        return self.__class__.__name__ + "(" + ", ".join(str(getattr(self, x)) for x in self.__class__._fields) + ")"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        try:
            return self.__class__ == other.__class__ \
                and all(getattr(self, x) == getattr(other, x) for x in self.__class__._fields)
        except:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

def _case_transform(tree):

    with q as methods:
        def __init__(self, *args, **kwargs):
            CaseClass.__init__(self, *args, **kwargs)

        _children = []
        _fields = []

    init_fun, set_children, set_fields = methods

    new_body = []
    new_classes = []

    for statement in tree.body:
        if type(statement) is ClassDef:
            new_body.append(_case_transform(statement))
            new_classes.append(Name(id = statement.name))
        elif type(statement) is FunctionDef:
            new_body.append(statement)
        else:
            init_fun.body.append(statement)

    set_children.value.elts = new_classes
    set_fields.value.elts = [Str(name.id) for name in tree.bases]
    tree.body = new_body
    tree.bases = [Name(id="CaseClass")]

    tree.body += methods
    tree.decorator_list.append(Name(id="link_children"))

    return tree

@macros.decorator()
def case(tree, **kw):
    return _case_transform(tree)
