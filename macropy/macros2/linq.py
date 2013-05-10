from ast import Call

from macropy.core.macros import *
from macropy.core.lift import macros, q, ast
from macropy.macros.quicklambda import macros, f
import sqlalchemy


macros = Macros()
@macros.expr
def sql(tree):
    x = replace_walk.recurse(recurse.recurse(tree, []))[0]
    print x
    return x

@macros.expr
def query(tree):
    x = replace_walk.recurse(recurse.recurse(tree, []))[0]
    return q%(lambda query: query.bind.execute(query).fetchall())(ast%x)


@ContextWalker
def recurse(tree, scope):
    if type(tree) is Compare and type(tree.ops[0]) is In:
        return q%(ast%recurse(tree.left)).in_(ast%recurse(tree.comparators[0])), [], []

    if type(tree) is GeneratorExp:

        aliases = map(f%_.target, tree.generators)
        tables = map(f%_.iter, tree.generators)

        aliased_tables = map(lambda x: q%((ast%x).alias().c), tables)

        ifs = [
            recurse.recurse(ifcond, [])[0]
            for gen in tree.generators
            for ifcond in gen.ifs
        ]

        elt = tree.elt
        if type(elt) is Tuple:
            sel = q%(ast_list%recurse.recurse(elt, [])[0].elts)
        else:
            sel = q%[ast%recurse.recurse(elt, [])[0]]

        out = q%select(ast%sel)


        for cond in ifs:
            out = q%(ast%out).where(ast%cond)

        if scope != []:
            out = q%(ast%out).as_scalar()

        out = q%(lambda x: ast%out)()
        out.func.args.args = aliases
        out.args = aliased_tables
        return out, stop, []

    return tree, [], []

def generate_schema(engine):
    metadata = sqlalchemy.MetaData(engine)
    metadata.reflect()
    class Db: pass
    db = Db()
    for table in metadata.sorted_tables:
        setattr(db, table.name, table)
    return db



@ContextWalker
def cfunc(tree, ctx):
    if type(tree) is Call and type(tree.func) is Lambda:
        return tree.func.body, stop, [tree]

    if type(tree) in [Lambda, GeneratorExp, ListComp, SetComp, DictComp]:
        return tree, stop, []

    return tree, [], []

@Walker
def replace_walk(tree):
    tree, chunks = cfunc.recurse(tree)
    for v in chunks:
        let_tree = v
        let_tree.func.body = tree
        tree = let_tree
    return tree
