from ast import Call

from macropy.core.macros import *
from macropy.core.quotes import macros, hq, ast, name
from macropy.quick_lambda import macros, f
import sqlalchemy

macros = Macros()

@macros.expr
def sql(tree, hygienic_alias, **kw):
    x = process(tree, hygienic_alias)
    x = expand_let_bindings.recurse(x)
    return x

@macros.expr
def query(tree, gen_sym, hygienic_alias, **kw):
    x = process(tree, hygienic_alias)
    x = expand_let_bindings.recurse(x)
    sym = gen_sym()
    # return q[(lambda query: query.bind.execute(query).fetchall())(ast[x])]
    new_tree = hq[(lambda query: name[sym].bind.execute(name[sym]).fetchall())(ast[x])]
    new_tree.func.args = arguments([Name(id=sym)], None, None, [])
    return new_tree

def process(tree, hygienic_alias):
    @Walker
    def recurse(tree, **kw):
        if type(tree) is Compare and type(tree.ops[0]) is In:
            return hq[(ast[tree.left]).in_(ast[tree.comparators[0]])]

        elif type(tree) is GeneratorExp:

            aliases = map(f[_.target], tree.generators)
            tables = map(f[_.iter], tree.generators)

            aliased_tables = map(lambda x: hq[(ast[x]).alias().c], tables)

            elt = tree.elt
            if type(elt) is Tuple:
                sel = hq[ast_list[elt.elts]]
            else:
                sel = hq[[ast[elt]]]

            out = hq[sqlalchemy.select(ast[sel])]

            for gen in tree.generators:
                for cond in gen.ifs:
                    out = hq[ast[out].where(ast[cond])]


            out = hq[(lambda x: ast[out])()]
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


@Walker
def _find_let_bindings(tree, ctx, stop, collect, **kw):
    if type(tree) is Call and type(tree.func) is Lambda:
        stop()
        collect(tree)
        return tree.func.body

    elif type(tree) in [Lambda, GeneratorExp, ListComp, SetComp, DictComp]:
        stop()
        return tree

@Walker
def expand_let_bindings(tree, **kw):
    tree, chunks = _find_let_bindings.recurse_collect(tree)
    for v in chunks:
        let_tree = v
        let_tree.func.body = tree
        tree = let_tree
    return tree

