from macropy.core.macros import *
from macropy.core import *
macros = Macros()

@singleton
class u(): pass

@singleton
class name(): pass

@singleton
class ast(): pass

@singleton
class ast_list(): pass

@singleton
class unhygienic(): pass


@Walker
def _unquote_search(tree, **kw):

    res = check_annotated(tree)
    if res:
        func, right = res

        if 'u' == func:
            return Literal(Call(Name(id="ast_repr"), [right], [], None, None))
        elif 'name' == func:
            return Literal(Call(Name(id="Name"), [], [keyword("id", right)], None, None))
        elif 'ast' == func:
            return Literal(right)
        elif 'ast_list' == func:
            return Literal(Call(Name(id="List"), [], [keyword("elts", right)], None, None))


@macros.expr()
def q(tree, **kw):
    tree = _unquote_search.recurse(tree)
    tree = ast_repr(tree)
    return tree

@macros.block()
def q(tree, target, **kw):
    body = _unquote_search.recurse(tree)
    new_body = ast_repr(body)
    return [Assign([Name(id=target.id)], new_body)]


@macros.block()
def hq(tree, module_alias, target, **kw):
    tree = _unquote_search.recurse(tree)
    tree = hygienate(tree, module_alias)
    tree1 = [With(Name(id='q'), target, tree)]

    return tree1

@macros.expr()
def hq(tree, module_alias, **kw):

    tree = _unquote_search.recurse(tree)
    tree = hygienate(tree, module_alias)
    tree = Subscript(Name(id="q"), Index(tree), Load())
    return tree

def hygienate(tree, module_alias):
    @Walker
    def hygienator(tree, stop, **kw):
        if type(tree) is Name and type(tree.ctx) is Load:
            stop()
            return parse_expr(
                "name[module_alias].macros.registered[u[macros.register(%s)]]" % tree.id
            )
        if type(tree) is Literal:
            stop()
            return Subscript(Name(id="ast"), Index(tree.body), Load())

        res = check_annotated(tree)
        if res:
            id, subtree = res
            if 'unhygienic' == id:
                stop()
                del tree.slice.value.ctx
                return tree.slice.value
    return hygienator.recurse(tree)