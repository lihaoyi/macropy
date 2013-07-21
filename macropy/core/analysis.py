from walkers import *

@Walker
def find_names(tree, collect, **kw):
    if isinstance(tree, Name):
        collect(tree.id)

@Walker
def find_assignments(tree, collect, stop, **kw):
    if type(tree) in [ClassDef, FunctionDef]:
        collect(tree.name)
        stop()
    if type(tree) is Assign:
        for x in find_names.collect(tree.targets):
            collect(x)


def extract_arg_names(args):
        return box(args.vararg) + \
               box(args.kwarg) + \
               [name for x in args.args for name in find_names.collect(x)]


def with_scope(func):
    def new_func(tree, set_ctx_for, scope=[], **kw):

        if type(tree) is Lambda:
            set_ctx_for(tree.body, scope=scope + extract_arg_names(tree.args))

        if type(tree) in (GeneratorExp, ListComp, SetComp, DictComp):
            iterator_vars = []
            for gen in tree.generators:
                set_ctx_for(gen.target, scope=scope + iterator_vars)
                set_ctx_for(gen.iter, scope=scope + iterator_vars)
                iterator_vars.extend(find_names.collect(gen.target))
                set_ctx_for(gen.ifs, scope=scope + iterator_vars)

            if type(tree) is DictComp:
                set_ctx_for(tree.key, scope=scope + iterator_vars)
                set_ctx_for(tree.value, scope=scope + iterator_vars)
            else:
                set_ctx_for(tree.elt, scope=scope + iterator_vars)

        if type(tree) is FunctionDef:
            set_ctx_for(tree.body, scope=scope+extract_arg_names(tree.args) + find_assignments.collect(tree.body))

        if type(tree) is ClassDef:
            set_ctx_for(tree.body, scope=scope+find_assignments.collect(tree.body))

        return func(tree, set_ctx_for=set_ctx_for, scope=scope, **kw)

    return new_func
