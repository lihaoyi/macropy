from macropy.core.macros import *
from macropy.core import *
from macropy.core.quotes import macros, q, _unquote_search, u, ast, ast_list, name


macros = Macros()

@singleton
class unhygienic(): pass


@macros.block
def hq(tree, hygienic_alias, target, **kw):
    tree = _unquote_search.recurse(tree)
    tree = hygienate(tree, hygienic_alias)
    new_body = ast_repr(tree)
    return [Assign([Name(id=target.id)], new_body)]


@macros.expr
def hq(tree, hygienic_alias, **kw):

    tree = _unquote_search.recurse(tree)
    tree = hygienate(tree, hygienic_alias)
    tree = ast_repr(tree)
    return tree


def hygienate(tree, hygienic_alias):
    @Walker
    def hygienator(tree, stop, **kw):
        if type(tree) is Name and type(tree.ctx) is Load:
            stop()
            return q[
                ast[name.wrap(q[hygienic_alias])]
                .macros
                .registered[
                    ast[u.wrap(q[macros.register(name[tree.id])])]
                ]
            ]

        if type(tree) is Literal:
            stop()
            return ast.wrap(tree.body)

        res = check_annotated(tree)
        if res:
            id, subtree = res
            if 'unhygienic' == id:
                stop()
                tree.slice.value.ctx = None
                return tree.slice.value
    return hygienator.recurse(tree)