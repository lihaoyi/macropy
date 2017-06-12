# -*- coding: utf-8 -*-
import ast

import sqlalchemy

from ..core.macros import Macros
from ..core.walkers import Walker

from ..core import Captured
from ..core.quotes import ast_literal, name
from ..core.hquotes import macros, hq, ast_list
from ..quick_lambda import macros, f, _

macros = Macros()

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
    new_tree = hq[(lambda query: name[sym].bind.execute(name[sym]).fetchall())(ast_literal[x])]
    new_tree.func.args = ast.arguments([ast.arg(sym, None)], None, [], [],
                                       None, [])
    return new_tree


def process(tree):
    @Walker
    def recurse(tree, **kw):
        if type(tree) is ast.Compare and type(tree.ops[0]) is ast.In:
            return hq[(ast_literal[tree.left]).in_(
                ast_literal[tree.comparators[0]])]

        elif type(tree) is ast.GeneratorExp:

            aliases = list(map(f[_.target], tree.generators))
            tables = map(f[_.iter], tree.generators)

            aliased_tables = list(map(lambda x: hq[(ast_literal[x]).alias().c],
                                      tables))

            elt = tree.elt
            if type(elt) is ast.Tuple:
                sel = hq[ast_list[elt.elts]]
            else:
                sel = hq[[ast_literal[elt]]]

            out = hq[sqlalchemy.select(ast_literal[sel])]

            for gen in tree.generators:
                for cond in gen.ifs:
                    out = hq[ast_literal[out].where(ast_literal[cond])]


            out = hq[(lambda x: ast_literal[out])()]
            out.func.args.args = [ast.arg(n.id, None) for n in aliases]
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
def _find_let_bindings(tree, stop, collect, **kw):
    if type(tree) is ast.Call and type(tree.func) is ast.Lambda:
        stop()
        collect(tree)
        return tree.func.body

    elif type(tree) in [ast.Lambda, ast.GeneratorExp, ast.ListComp,
                        ast.SetComp, ast.DictComp]:
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
