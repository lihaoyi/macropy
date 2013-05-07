from macropy.core.macros import Macros
from macropy.core.core import *
from macropy.core.lift import macros, q, u, name, ast
from macropy.macros.quicklambda import macros, f
from ast import *
from macropy.core.util import *

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
            if tree.value.id in map(f%_[0], scope):
                column_getter = Attribute(
                    value=Name(id = dict(scope)[tree.value.id]),
                    attr='c',
                    ctx = Load()
                )
                tree.value = column_getter
                return tree
            else:
                return tree

        if type(tree) is GeneratorExp:

            aliases = map(f%_.target, tree.generators)
            tables = map(f%_.iter, tree.generators)
            import random

            aliased_tables = map(lambda x: q%((ast%x).alias().c), tables)

            ifs = [
                recurse(ifcond, scope)
                for gen in tree.generators
                for ifcond in gen.ifs
            ]

            elt = tree.elt
            if type(elt) is Tuple:

                sel = q%(ast_list%recurse(elt, scope).elts)
            else:
                sel = q%[ast%recurse(elt, scope)]


            out = q%select(ast%sel)

            for cond in ifs:
                out = q%(ast%out).where(ast%cond)
            out = q%(lambda x: ast%out)()
            out.func.args.args = aliases
            out.args = aliased_tables
            return out

        return tree

    x = recurse(tree, [])
    return x

