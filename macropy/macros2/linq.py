from ast import Call

from macropy.core.macros import *
from macropy.core.lift import macros, q, ast
from macropy.macros.quicklambda import macros, f
import sqlalchemy


"""
Aggregate Functions:
    http://www.sqlite.org/lang_aggfunc.html
    avg(x)                  linq.avg
    count(x)                linq.count
    group_concat(x)
    group_concat(x, y)
    max(x)                  max
    min(x)                  min
    sum(x)                  sum
    total(x)                linq.total

Core Functions:
    http://www.sqlite.org/lang_corefunc.html
    abs(x)                  abs
    changes()
    char(x1, x2, ..., xn)
    coalesce(x, y, ...)
    glob(x, y)
    ifnull(x, y)
    instr(x, y)
    hex(x)                  hex
    last_insert_rowid()
    length(x)               len
    like(x, y)
    like(x, y, z)
    load_extension(x)
    load_extension(x, y)
    lower(x)                str.lower
    ltrim(x)                str.lstrip
    ltrim(x, y)             str.lstrip
    max(x, y, ...)          max
    min(x, y, ...)          min
    nullif(x, y)
    quote(x)
    random()                linq.random
    randomblob(n)
    replace(x, y, z)        str.replace
    round(x)                round
    round(x, y)             round
    rtrim(x)                str.rstrip
    rtrim(x, y)             str.rstrip
    soundex(x)
    sqlite_compileoption_get(n)
    sqlite_comileoption_used(x)
    sqlite_source_id()
    sqlite_version()
    substr(x, y, z)         str[:]
    substr(x, y)            str[:]
    total_changes()
    trim(x)                 str.strip
    trim(x, y)              str.strip
    typeof(x)
    unicode(x)
    upper(x)                str.upper
    zeroblob(n)
"""
macros = Macros()
@macros.expr
def sql(tree):
    x = replace_walk.recurse(recurse(tree, []))
    return x

@macros.expr
def query(tree):
    x = replace_walk.recurse(recurse(tree, []))
    return q%(lambda query: query.bind.execute(query).fetchall())(ast%x)


def recurse(tree, scope):
    if type(tree) is Compare and type(tree.ops[0]) is In:
        return q%(ast%recurse(tree.left, scope)).in_(ast%recurse(tree.comparators[0], scope))

    if type(tree) is Compare:
        tree.left = recurse(tree.left, scope)
        tree.comparators = map(f%recurse(_, scope), tree.comparators)
        return tree

    if type(tree) is Call:
        tree.func = recurse(tree.func, scope)
        tree.args = map(f%recurse(_, scope), tree.args)
        return tree

    if type(tree) is BinOp:
        tree.left = recurse(tree.left, scope)
        tree.right = recurse(tree.right, scope)
        return tree

    if type(tree) is BoolOp:
        tree.values = map(f%recurse(_, scope), tree.values)
        return tree

    if type(tree) is Tuple:
        tree.elts = map(f%recurse(_, scope), tree.elts)

    if type(tree) is Attribute:

        tree.value = recurse(tree.value, scope)
        return tree

    if type(tree) is GeneratorExp:

        aliases = map(f%_.target, tree.generators)
        tables = map(f%_.iter, tree.generators)

        aliased_tables = map(lambda x: q%((ast%x).alias().c), tables)

        ifs = [
            recurse(ifcond, None)
            for gen in tree.generators
            for ifcond in gen.ifs
        ]

        elt = tree.elt
        if type(elt) is Tuple:

            sel = q%(ast_list%recurse(elt, None).elts)
        else:
            sel = q%[ast%recurse(elt, None)]

        out = q%select(ast%sel)


        for cond in ifs:
            out = q%(ast%out).where(ast%cond)

        if scope != []:
            out = q%(ast%out).as_scalar()

        out = q%(lambda x: ast%out)()
        out.func.args.args = aliases
        out.args = aliased_tables
        return out

    return tree

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
