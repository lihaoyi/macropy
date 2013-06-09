from macropy.core.macros import *
from macropy.core import *
macros = Macros()

macros.expose()(Literal)

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

    if isinstance(tree, Subscript) and \
                    type(tree.slice) is Index and \
                    type(tree.value) is Name:

        func, right = tree.value.id, tree.slice.value

        if 'u' == func:
            return Literal(Call(Name(id="ast_repr"), [right], [], None, None))
        elif 'name' == func:
            return Literal(Call(Name(id="Name"), [], [keyword("id", right)], None, None))
        elif 'ast' == func:
            return Literal(right)
        elif 'ast_list' == func:
            return Literal(Call(Name(id="List"), [], [keyword("elts", right)], None, None))


@macros.expr()
def q(tree, hygienic_names, **kw):
    tree = _unquote_search.recurse(tree)
    tree = Call(
        func=Name(id=hygienic_names("rename"), ctx=Load()),
        args=[ast_repr(tree), Name(id="hygienic_names", ctx=Load())],
        keywords=[],
        starargs=None,
        kwargs=None
    )
    return tree

@macros.block()
def q(tree, target, hygienic_names, **kw):
    body = _unquote_search.recurse(tree)
    new_body = Call(
        func=Name(id=hygienic_names("rename"), ctx=Load()),
        args=[ast_repr(body), Name(id="hygienic_names", ctx=Load())],
        keywords=[],
        starargs=None,
        kwargs=None
    )
    return [Assign([Name(id=target.id)], new_body)]

@macros.expose()
def rename(tree, hygienic_names):
    @Walker
    def renamer(tree, stop, **kw):
        if type(tree) is Name:
            tree.id = hygienic_names(tree.id)
        if type(tree) is Literal:
            stop()
            return tree.body
    return renamer.recurse(tree)



@macros.expose_unhygienic()
def hygienic_names(x):
    return x


@macros.block()
def hq(tree, module_alias, target, **kw):
    tree = _unquote_search.recurse(tree)
    tree = hygienate(tree, module_alias)
    tree1 = [With(
        Name(id='q'),
        target,
        tree
    )]
    tree2 = parse_stmt("with q as %s:\n%s" % (target.id, unparse_ast(tree).replace("\n", "\n    ")))

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
                "name[module_alias].macros.registered[u[macros.register(%s)]]" % (tree.id)
            )
        if type(tree) is Literal:
            stop()
            return parse_expr("ast[%s]" % unparse_ast(tree.body))
        if isinstance(tree, Subscript) and \
                    type(tree.slice) is Index and \
                    type(tree.value) is Name:


            if 'unhygienic' == tree.value.id:
                stop()
                del tree.slice.value.ctx
                return tree.slice.value
    return hygienator.recurse(tree)