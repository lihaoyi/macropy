# -*- coding: utf-8 -*-
import ast

import sqlalchemy

from ..core.macros import Macros
from ..core.walkers import Walker

from ..core import Captured  # noqa: F401
from ..core.quotes import ast_literal, name
from ..core.hquotes import macros, hq, ast_list
from ..quick_lambda import macros, f, _  # noqa: F401,F811


macros = Macros()  # noqa: F811


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
    new_tree = hq[(lambda query: name[sym].bind.execute(
        name[sym]).fetchall())(ast_literal[x])]
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
            elt_aliases = []
            arg_names = []
            call_params = []
            for gen in tree.generators:
                elt_alias = gen.target
                it = gen.iter
                table_alias = hq[ast_literal[it]
                                 if isinstance(ast_literal[it],
                                               sqlalchemy.sql.Alias)
                                 else ast_literal[it].alias()]
                cols = hq[ast_literal[table_alias].c]
                elt_aliases.append(elt_alias)

                arg_names.extend((ast.Name(id=(elt_alias.id+'_alias'),
                                           ctx=ast.Load()),
                                  elt_alias))
                call_params.extend((table_alias, cols))

            elt = tree.elt
            if type(tree.elt) is ast.Tuple:
                sel = hq[ast_list[elt.elts]]
            else:
                sel = hq[[ast_literal[elt]]]

            out = hq[sqlalchemy.select(ast_literal[sel])]

            # take care of ifs in the genexpr
            for gen in tree.generators:
                for cond in gen.ifs:
                    out = hq[ast_literal[out].where(ast_literal[cond])]

            # if there are varnames that match a genexpr target that
            # aren't subject of attribute get (like accessing column
            # names), replace those with `<varname>_alias`. In this
            # way the ``sqlalchemy.select()`` function will perform the
            # equivalent of a ``SELECT * FROM bar`` while respecting
            # the presence of multiple aliased tables.
            fix_columns.recurse(out, elt_aliases=elt_aliases)

            # 'out' is an ast.Call object where out.func is an
            # ast.Lambda taking a single param 'x'
            out = hq[(lambda x: ast_literal[out])()]

            # this replaces the 'x' param with the name of the targets
            # on each generator expression (the foo in 'for foo in
            # bar'). Each genexpr produces two arg names: ``foo_alias,
            # foo``.
            out.func.args.args = [ast.arg(n.id, None) for n in arg_names]
            # this replaces the ast.Call arguments with the
            # ``sqlalchemy.alias()`` calculated for each iterable the
            # (the bar in 'for foo in bar'). Each genexpr will produce
            # two args, the first is the aliased selectable and the
            # second its columns
            out.args = call_params
            return out
    return recurse.recurse(tree)


def generate_schema(engine):
    metadata = sqlalchemy.MetaData(engine)
    metadata.reflect()

    class Db:
        pass
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


@Walker
def fix_columns(tree, stop, elt_aliases, **kw):
    """if the "columns" name isn't attribute accessed, replace it with the
    same name witn '_alias' appended."""
    if (type(tree) is ast.Attribute and type(tree.value) is ast.Name
        and any(map(lambda elt: elt.id == tree.value.id, elt_aliases))):
        stop()
        return tree
    elif (type(tree) is ast.Name and
          any(map(lambda elt: elt.id == tree.id, elt_aliases))):
        stop()
        return ast.Name(id=(tree.id+'_alias'), ctx=ast.Load())
    else:
        return tree
