import macropy.activate
from define_dictdock import *
a = DictDock()
b = DictDock()
print a == b # True
a.d['foo'] = 'bar'
print a      # DictDock({'foo': 'bar'})
print b      # DictDock({'foo': 'bar'})
print a == b # True
