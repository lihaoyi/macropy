"""Macro to allow for Coffeescript/ES6-style object literal shorthand via `d` function, a la
  `d(name, age, other=thing) == {"name": name, "age": age, "other": thing}`
"""

from macropy.core.macros import *

macros = Macros()


@macros.expr
def d(*args, **kw):
    """ use in place of dict() to mix positional & keyword args) """
    tree = kw["tree"]
    keywordified_args = [keyword(arg.id, arg) for arg in tree.args]
    return Call(Name('dict', Load()), [], tree.keywords + keywordified_args, None, None)
