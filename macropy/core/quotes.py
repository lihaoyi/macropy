from macropy.core.macros import *
from macropy.core import *
macros = Macros()



@macros.expose_transient()
@singleton
class u(): pass

@macros.expose_transient()
@singleton
class name(): pass

@macros.expose_transient()
@singleton
class ast(): pass

@macros.expose_transient()
@singleton
class ast_list(): pass

@Walker
def _unquote_search(tree, **kw):
    if isinstance(tree, Subscript) and type(tree.slice) is Index:

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
def q(tree, **kw):
    tree = _unquote_search.recurse(tree)
    return Call(
        func=Name(id="rename", ctx=Load()),
        args=[ast_repr(tree), Name(id="hygienic_names", ctx=Load())],
        keywords=[],
        starargs=None,
        kwargs=None
    )

@macros.block()
def q(tree, target, **kw):
    body = _unquote_search.recurse(tree)
    new_body = Call(
        func=Name(id="rename", ctx=Load()),
        args=[ast_repr(body), Name(id="hygienic_names", ctx=Load())],
        keywords=[],
        starargs=None,
        kwargs=None
    )
    return [Assign([Name(id=target.id)], new_body)]

@macros.expose_unhygienic()
def rename(tree, hygienic_names):
    @Walker
    def renamer(tree, **kw):
        if type(tree) is Name:
            tree.id = hygienic_names(tree.id)
    return renamer.recurse(tree)



@macros.expose_unhygienic()
def hygienic_names(x):
    return x