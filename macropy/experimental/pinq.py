import ast

import macropy.core.macros
import macropy.core.walkers

from macropy.core.hquotes import macros, hq, ast_splice, name, ast_list
from macropy.quick_lambda import macros, f, _
import sqlalchemy

macros = macropy.core.macros.Macros()

# workaround for inability to pickle modules



@macros.expr
def sql(tree, **kw):
    x = process(tree)
    x = expand_let_bindings.recurse(x)

    return x

@macros.expr
def query(tree, gen_sym, **kw):
    x = process(tree)
    x = expand_let_bindings.recurse(x)
    sym = gen_sym()
    # return q[(lambda query: query.bind.execute(query).fetchall())(ast[x])]
    new_tree = hq[(lambda query: name[sym].bind.execute(name[sym]).fetchall())(ast_splice[x])]
    new_tree.func.args = ast.arguments([ast.Name(id=sym)], None, None, [])
    return new_tree


def process(tree):
    @macropy.core.walkers.Walker
    def recurse(tree, **kw):
        if type(tree) is ast.Compare and type(tree.ops[0]) is ast.In:
            return hq[(ast_splice[tree.left]).in_(ast_splice[tree.comparators[0]])]

        elif type(tree) is ast.GeneratorExp:

            aliases = list(map(f[_.target], tree.generators))
            tables = map(f[_.iter], tree.generators)

            aliased_tables = list(map(lambda x: hq[(ast_splice[x]).alias().c], tables))

            elt = tree.elt
            if type(elt) is ast.Tuple:
                sel = hq[ast_list[elt.elts]]
            else:
                sel = hq[[ast_splice[elt]]]

            out = hq[sqlalchemy.select(ast_splice[sel])]

            for gen in tree.generators:
                for cond in gen.ifs:
                    out = hq[ast_splice[out].where(ast_splice[cond])]


            out = hq[(lambda x: ast_splice[out])()]
            out.func.args.args = aliases
            out.args = aliased_tables
            return out
    return recurse.recurse(tree)

def generate_schema(engine):
    metadata = sqlalchemy.MetaData(engine)
    metadata.reflect()
    class Db: pass
    db = Db()
    for table in metadata.sorted_tables:
        setattr(db, table.name, table)
    return db


@macropy.core.walkers.Walker
def _find_let_bindings(tree, ctx, stop, collect, **kw):
    if type(tree) is ast.Call and type(tree.func) is ast.Lambda:
        stop()
        collect(tree)
        return tree.func.body

    elif type(tree) in [ast.Lambda, ast.GeneratorExp, ast.ListComp, ast.SetComp, ast.DictComp]:
        stop()
        return tree

@macropy.core.walkers.Walker
def expand_let_bindings(tree, **kw):
    tree, chunks = _find_let_bindings.recurse_collect(tree)
    for v in chunks:
        let_tree = v
        let_tree.func.body = tree
        tree = let_tree
    return tree

