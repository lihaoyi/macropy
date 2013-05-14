from ast import Call

from macropy.core.macros import *
from macropy.core.lift import macros, q, ast
from macropy.macros.quicklambda import f
import sqlalchemy


macros = Macros()

@macros.expr()
def sql(tree):
    x = _recurse.recurse(tree)
    x = expand_let_bindings.recurse(x)
    return x

@macros.expr()
def query(tree):
    x = _recurse.recurse(tree)
    x = expand_let_bindings.recurse(x)
    return q%(lambda query: query.bind.execute(query).fetchall())(ast%x)


@Walker
def _recurse(tree):
    if type(tree) is Compare and type(tree.ops[0]) is In:
        return q%(ast%tree.left).in_(ast%tree.comparators[0])

    elif type(tree) is GeneratorExp:

        aliases = map(f%_.target, tree.generators)
        tables = map(f%_.iter, tree.generators)

        aliased_tables = map(lambda x: q%((ast%x).alias().c), tables)

        elt = tree.elt
        if type(elt) is Tuple:
            sel = q%(ast_list%elt.elts)
        else:
            sel = q%[ast%elt]

        out = q%select(ast%sel)

        for gen in tree.generators:
            for cond in gen.ifs:
                out = q%(ast%out).where(ast%cond)


        out = q%(lambda x: ast%out)()
        out.func.args.args = aliases
        out.args = aliased_tables
        return out


def generate_schema(engine):
    metadata = sqlalchemy.MetaData(engine)
    metadata.reflect()
    class Db: pass
    db = Db()
    for table in metadata.sorted_tables:
        setattr(db, table.name, table)
    return db


@Walker
def _find_let_bindings(tree, ctx):
    if type(tree) is Call and type(tree.func) is Lambda:
        return tree.func.body, stop, collect(tree)

    elif type(tree) in [Lambda, GeneratorExp, ListComp, SetComp, DictComp]:
        return tree, stop

@Walker
def expand_let_bindings(tree):
    tree, chunks = _find_let_bindings.recurse_real(tree)
    for v in chunks:
        let_tree = v
        let_tree.func.body = tree
        tree = let_tree
    return tree

