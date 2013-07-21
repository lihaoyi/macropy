import unittest
from walkers import Walker
from macropy.core.analysis import with_scope
from macropy.core import *

@Walker
@with_scope
def scoped(tree, scope, collect, **kw):
    try:
        collect((unparse(tree), scope))
    except:
        pass

class Tests(unittest.TestCase):
    def test_simple_expr(self):
        tree = parse_expr("(lambda x: a)")
        assert scoped.collect(tree) == [
            ('(lambda x: a)', []),
            ('x', []),
            ('x', []),
            ('a', ['x'])
        ]

        tree = parse_expr("(lambda x, y: (lambda z: a))")
        assert scoped.collect(tree) == [
            ('(lambda x, y: (lambda z: a))', []),
            ('x, y', []),
            ('x', []),
            ('y', []),
            ('(lambda z: a)', ['x', 'y']),
            ('z', ['x', 'y']),
            ('z', ['x', 'y']),
            ('a', ['x', 'y', 'z']),
        ]


        tree = parse_expr("[e for (a, b) in c for d in e if f]")
        assert scoped.collect(tree) == [
            ('[e for (a, b) in c for d in e if f]', []),
            ('e', ['a', 'b', 'd']),
            (' for (a, b) in c', []),
            ('(a, b)', []),
            ('a', []),
            ('b', []),
            ('c', []),
            (' for d in e if f', []),
            ('d', ['a', 'b']),
            ('e', ['a', 'b']),
            ('f', ['a', 'b', 'd'])
        ]

        tree = parse_expr("{k: v for k, v in d}")
        assert scoped.collect(tree) == [
            ('{k: v for (k, v) in d}', []),
            ('k', ['k', 'v']),
            ('v', ['k', 'v']),
            (' for (k, v) in d', []),
            ('(k, v)', []),
            ('k', []),
            ('v', []),
            ('d', [])
        ]
    def test_simple_stmt(self):
        tree = parse_stmt("""
def func(x, y):
    return x
        """)
        assert scoped.collect(tree) == [
            ('\n\ndef func(x, y):\n    return x', []),
            ('x, y', []),
            ('x', []),
            ('y', []),
            ('\nreturn x', ['x', 'y']),
            ('x', ['x', 'y'])
        ]

        tree = parse_stmt("""
def func(x, y):
    z = 10
    return x
        """)
        assert scoped.collect(tree) == [
            ('\n\ndef func(x, y):\n    z = 10\n    return x', []),
            ('x, y', []),
            ('x', []),
            ('y', []),
            ('\nz = 10', ['x', 'y', 'z']),
            ('z', ['x', 'y', 'z']),
            ('10', ['x', 'y', 'z']),
            ('\nreturn x', ['x', 'y', 'z']),
            ('x', ['x', 'y', 'z'])
        ]

        tree = parse_stmt("""
class C(A, B):
    z = 10
    print z
        """)
        assert scoped.collect(tree) == [
            ('\n\nclass C(A, B):\n    z = 10\n    print z', []),
            ('A', []),
            ('B', []),
            ('\nz = 10', ['z']),
            ('z', ['z']),
            ('10', ['z']),
            ('\nprint z', ['z']),
            ('z', ['z'])
        ]

        tree = parse_stmt("""
def func(x, y):
    def do_nothing(): pass
    class C(): pass
    print 10
        """)
        assert scoped.collect(tree) == [
            ('\n\ndef func(x, y):\n\n    def do_nothing():\n        pass\n\n    class C:\n        pass\n    print 10', []),
            ('x, y', []),
            ('x', []),
            ('y', []),
            ('\n\ndef do_nothing():\n    pass', ['x', 'y', 'do_nothing', 'C']),
            ('', ['x', 'y', 'do_nothing', 'C']),
            ('\npass', ['x', 'y', 'do_nothing', 'C']),
            ('\n\nclass C:\n    pass', ['x', 'y', 'do_nothing', 'C']),
            ('\npass', ['x', 'y', 'do_nothing', 'C']),
            ('\nprint 10', ['x', 'y', 'do_nothing', 'C']),
            ('10', ['x', 'y', 'do_nothing', 'C'])
        ]
        print ",\n".join(map(str, scoped.collect(tree)))
