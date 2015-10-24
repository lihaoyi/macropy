from macropy.case_classes import macros, case
@case
class DictDock(d | {}):
    pass

from macropy.tracing import macros, trace
with trace:
    a = DictDock()   # new instance
    b = DictDock()   # new instance
    a == b           # their contents are equal and empty
    a is b           # but they're different identities
    a.d is b.d       # and their dict's have the same ident
a.d['foo'] = 'bar'   # put something in a's dictionary
with trace:
    a.d['foo']       # the 'something' is in a's dictionary
    b.d['foo']       # but it's in b's dictionary too
    a == b           # their contents are still equal
    a is b           # and they're still not the same
    a.d is b.d       # their dict's are still same ident
with trace:
    g = DictDock({}) # new instance; explicit initializer
    h = DictDock({}) # new instance; explicit initializer
    g.d is h.d       # different dictionaries inside
g.d['x'] = 42        # put something in g's dict
with trace:
    g.d              # check g's dict
    h.d              # check h's dict
