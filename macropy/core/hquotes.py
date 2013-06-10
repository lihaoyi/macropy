from macropy.core.macros import *
from macropy.core import *
from macropy.core.quotes import _unquote_search, u, ast, ast_list, name

macros = Macros()

@singleton
class unhygienic(): pass


@macros.block
def hq(tree, hygienic_alias, target, **kw):
    tree = _unquote_search.recurse(tree)
    tree = hygienate(tree, hygienic_alias)
    body = _unquote_search.recurse(tree)
    new_body = ast_repr(body)
    return [Assign([Name(id=target.id)], new_body)]


@macros.expr
def hq(tree, hygienic_alias, **kw):

    tree = _unquote_search.recurse(tree)
    tree = hygienate(tree, hygienic_alias)
    tree = _unquote_search.recurse(tree)
    tree = ast_repr(tree)
    return tree


def hygienate(tree, hygienic_alias):
    @Walker
    def hygienator(tree, stop, **kw):
        if type(tree) is Name and type(tree.ctx) is Load:
            stop()
            return parse_expr(
                "name[hygienic_alias].macros.registered[u[macros.register(%s)]]"
                % tree.id
            )
        if type(tree) is Literal:
            stop()
            return Subscript(Name(id="ast"), Index(tree.body), Load())

        res = check_annotated(tree)
        if res:
            id, subtree = res
            if 'unhygienic' == id:
                stop()
                tree.slice.value.ctx = None
                return tree.slice.value
    return hygienator.recurse(tree)