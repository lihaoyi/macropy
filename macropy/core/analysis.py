from walkers import *
from macropy.core import merge_dicts

@Walker
def find_names(tree, collect, stop, **kw):
    if type(tree) in [Attribute, Subscript]:
        stop()
    if isinstance(tree, Name):
        collect((tree.id, tree))

@Walker
def find_assignments(tree, collect, stop, **kw):
    if type(tree) in [ClassDef, FunctionDef]:
        collect((tree.name, tree))
        stop()
    if type(tree) is Assign:
        for x in find_names.collect(tree.targets):
            collect(x)


def extract_arg_names(args):
    return dict(
        ([(args.vararg.id, args.vararg)] if args.vararg else []) +
        ([(args.kwarg.id, args.kwarg)] if args.kwarg else []) +
        [pair for x in args.args for pair in find_names.collect(x)]
    )


def with_scope(func):
    def new_func(tree, set_ctx_for, scope={}, **kw):

        if type(tree) is Lambda:
            set_ctx_for(tree.body, scope=merge_dicts(scope, extract_arg_names(tree.args)))

        if type(tree) in (GeneratorExp, ListComp, SetComp, DictComp):
            iterator_vars = {}
            for gen in tree.generators:
                set_ctx_for(gen.target, scope=merge_dicts(scope, iterator_vars))
                set_ctx_for(gen.iter, scope=merge_dicts(scope, iterator_vars))
                iterator_vars.update(dict(find_names.collect(gen.target)))
                set_ctx_for(gen.ifs, scope=merge_dicts(scope, iterator_vars))

            if type(tree) is DictComp:
                set_ctx_for(tree.key, scope=merge_dicts(scope, iterator_vars))
                set_ctx_for(tree.value, scope=merge_dicts(scope, iterator_vars))
            else:
                set_ctx_for(tree.elt, scope=merge_dicts(scope, iterator_vars))

        if type(tree) is FunctionDef:

            set_ctx_for(tree.args, scope=merge_dicts(scope, {tree.name: tree}))
            new_scope = merge_dicts(
                scope,
                {tree.name: tree},
                extract_arg_names(tree.args),
                dict(find_assignments.collect(tree.body)),
            )

            set_ctx_for(tree.body, scope=new_scope)

        if type(tree) is ClassDef:
            set_ctx_for(tree.body, scope=merge_dicts(scope, dict(find_assignments.collect(tree.body))))

        if type(tree) is ExceptHandler:
            set_ctx_for(tree.body, scope=merge_dicts(scope, {tree.name.id: tree.name}))

        return func(tree, set_ctx_for=set_ctx_for, scope=scope, **kw)

    return new_func
