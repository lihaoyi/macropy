import unittest
from walkers import Walker
from macropy.core.analysis import with_scope
from macropy.core import *
import ast

@with_scope
@Walker
def scoped(tree, scope, collect, **kw):
    try:
        if scope != {}:
            collect((unparse(tree), {k: type(v) for k, v in scope.items()}))
    except:
        pass

class Tests(unittest.TestCase):
    def test_simple_expr(self):
        tree = parse_expr("(lambda x: a)")

        assert scoped.collect(tree) == [('a', {'x': ast.Name})]

        tree = parse_expr("(lambda x, y: (lambda z: a))")

        assert scoped.collect(tree) == [
            ('(lambda z: a)', {'y': ast.Name, 'x': ast.Name}),
            ('z', {'y': ast.Name, 'x': ast.Name}),
            ('z', {'y': ast.Name, 'x': ast.Name}),
            ('a', {'y': ast.Name, 'x': ast.Name, 'z': ast.Name})
        ]

        tree = parse_expr("[e for (a, b) in c for d in e if f]")

        assert scoped.collect(tree) == [
            ('e', {'a': ast.Name, 'b': ast.Name, 'd': ast.Name}),
            ('d', {'a': ast.Name, 'b': ast.Name}),
            ('e', {'a': ast.Name, 'b': ast.Name}),
            ('f', {'a': ast.Name, 'b': ast.Name, 'd': ast.Name})
        ]


        tree = parse_expr("{k: v for k, v in d}")

        assert scoped.collect(tree) == [
            ('k', {'k': ast.Name, 'v': ast.Name}),
            ('v', {'k': ast.Name, 'v': ast.Name})
        ]

    def test_simple_stmt(self):
        tree = parse_stmt("""
def func(x, y):
    return x
        """)

        assert scoped.collect(tree) == [
            ('\n\ndef func(x, y):\n    return x', {'func': ast.FunctionDef}),
            ('x, y', {'func': ast.FunctionDef}),
            ('x', {'func': ast.FunctionDef}),
            ('y', {'func': ast.FunctionDef}),
            ('\nreturn x', {'y': ast.Name, 'x': ast.Name, 'func': ast.FunctionDef}),
            ('x', {'y': ast.Name, 'x': ast.Name, 'func': ast.FunctionDef})
        ]

        tree = parse_stmt("""
def func(x, y):
    z = 10
    return x
        """)

        assert scoped.collect(tree) == [
            ('\n\ndef func(x, y):\n    z = 10\n    return x', {'func': ast.FunctionDef}),
            ('x, y', {'func': ast.FunctionDef}),
            ('x', {'func': ast.FunctionDef}),
            ('y', {'func': ast.FunctionDef}),
            ('\nz = 10', {'y': ast.Name, 'x': ast.Name, 'z': ast.Name, 'func': ast.FunctionDef}),
            ('z', {'y': ast.Name, 'x': ast.Name, 'z': ast.Name, 'func': ast.FunctionDef}),
            ('10', {'y': ast.Name, 'x': ast.Name, 'z': ast.Name, 'func': ast.FunctionDef}),
            ('\nreturn x', {'y': ast.Name, 'x': ast.Name, 'z': ast.Name, 'func': ast.FunctionDef}),
            ('x', {'y': ast.Name, 'x': ast.Name, 'z': ast.Name, 'func': ast.FunctionDef})
        ]

        tree = parse_stmt("""
class C(A, B):
    z = 10
    print z
        """)

        print ",\n".join(map(str, scoped.collect(tree)))
        assert scoped.collect(tree) == [
            ('\nz = 10', {'z': ast.Name}),
            ('z', {'z': ast.Name}),
            ('10', {'z': ast.Name}),
            ('\nprint z', {'z': ast.Name}),
            ('z', {'z': ast.Name})
        ]

        tree = parse_stmt("""
def func(x, y):
    def do_nothing(): pass
    class C(): pass
    print 10
        """)


        assert scoped.collect(tree) == [
            ('x, y', {'func': ast.FunctionDef}),
            ('x', {'func': ast.FunctionDef}),
            ('y', {'func': ast.FunctionDef}),
            ('\n\ndef do_nothing():\n    pass', {'y': ast.Name, 'x': ast.Name, 'C': ast.ClassDef, 'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef}),
            ('', {'y': ast.Name, 'x': ast.Name, 'C': ast.ClassDef, 'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef}),
            ('\npass', {'y': ast.Name, 'x': ast.Name, 'C': ast.ClassDef, 'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef}),
            ('\n\nclass C:\n    pass', {'y': ast.Name, 'x': ast.Name, 'C': ast.ClassDef, 'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef}),
            ('\npass', {'y': ast.Name, 'x': ast.Name, 'C': ast.ClassDef, 'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef}),
            ('\nprint 10', {'y': ast.Name, 'x': ast.Name, 'C': ast.ClassDef, 'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef}),
            ('10', {'y': ast.Name, 'x': ast.Name, 'C': ast.ClassDef, 'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef})
        ]

        tree = parse_stmt("""
try:
    pass
except Exception as e:
    pass
        """)

        assert scoped.collect(tree) == [
            ('\npass', {'e': ast.Name})
        ]

        tree = parse_stmt("""
C = 1
class C:
    C
C
        """)
        print scoped.collect(tree)