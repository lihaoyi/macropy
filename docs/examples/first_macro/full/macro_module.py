# -*- coding: utf-8 -*-
import ast

from macropy.core.macros import Macros
from macropy.core.quotes import macros, q, ast_literal
from macropy.core.walkers import Walker

_ = None  # makes IDE happy


macros = Macros()  # noqa: F811


@macros.expr
def f(tree, **kw):
    names = ('arg' + str(i) for i in range(100))

    @Walker
    def underscore_search(tree, collect, **kw):
        if isinstance(tree, ast.Name) and tree.id == "_":
            name = next(names)
            tree.id = name
            collect(name)
            return tree

    tree, used_names = underscore_search.recurse_collect(tree)

    new_tree = q[lambda: ast_literal[tree]]
    new_tree.args.args = [ast.arg(arg=x) for x in used_names]
    return new_tree
