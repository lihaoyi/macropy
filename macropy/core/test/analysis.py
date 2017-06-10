# -*- coding: utf-8 -*-
import ast
import unittest

import macropy.core

from macropy.core.walkers import Walker
from macropy.core.analysis import Scoped, extract_arg_names


@Scoped
@Walker
def scoped(tree, scope, collect, **kw):
    try:
        if scope != {}:
            collect((macropy.core.unparse(tree),
                     {k: type(v) for k, v in scope.items()}))
    except (AttributeError, KeyError):
        # TODO: This is ignoring a bunch of errors related to the
        # unparser not knowing how to unparse some elements of Python
        # code.
        pass


class Tests(unittest.TestCase):

    def test_extract_arg_names(self):
        from ast import parse, dump
        expr = parse("lambda a, b, f=6, *c, e=7, **d: 5")
        args = expr.body[0].value.args
        arg_names = extract_arg_names(args)
        convert_dict = lambda d: dict((k,v) if isinstance(v, str)
                                      else (k, dump(v)) for k, v in d.items())
        self.assertEqual(convert_dict({
            'a': "arg(arg='a', annotation=None)",
            'b': "arg(arg='b', annotation=None)",
            'c': "arg(arg='c', annotation=None)",
            'd': "arg(arg='d', annotation=None)",
            'e': "arg(arg='e', annotation=None)",
            'f': "arg(arg='f', annotation=None)"
        }), convert_dict(arg_names))

    def test_simple_expr(self):
        tree = macropy.core.parse_expr("(lambda x: a)")

        self.assertEqual(scoped.collect(tree), [('a', {'x': ast.arg})])

        tree = macropy.core.parse_expr("(lambda x, y: (lambda z: a))")

        self.assertEqual(scoped.collect(tree), [
            ('(lambda z: a)', {'y': ast.arg, 'x': ast.arg}),
            ('z', {'y': ast.arg, 'x': ast.arg}),
            ('z', {'y': ast.arg, 'x': ast.arg}),
            ('a', {'y': ast.arg, 'x': ast.arg, 'z': ast.arg})
        ])

        tree = macropy.core.parse_expr("[e for (a, b) in c for d in e if f]")

        self.assertEqual(scoped.collect(tree), [
            ('e', {'a': ast.Name, 'b': ast.Name, 'd': ast.Name}),
            ('d', {'a': ast.Name, 'b': ast.Name}),
            ('e', {'a': ast.Name, 'b': ast.Name}),
            ('f', {'a': ast.Name, 'b': ast.Name, 'd': ast.Name})
        ])


        tree = macropy.core.parse_expr("{k: v for k, v in d}")

        self.assertEqual(scoped.collect(tree), [
            ('k', {'k': ast.Name, 'v': ast.Name}),
            ('v', {'k': ast.Name, 'v': ast.Name})
        ])

    def test_simple_stmt(self):
        tree = macropy.core.parse_stmt("""
def func(x, y):
    return x
        """)

        self.assertEqual(scoped.collect(tree), [
            ('\n\ndef func(x, y):\n    return x', {'func': ast.FunctionDef}),
            ('x, y', {'func': ast.FunctionDef}),
            ('x', {'func': ast.FunctionDef}),
            ('y', {'func': ast.FunctionDef}),
            ('\nreturn x', {'y': ast.arg, 'x': ast.arg,
                            'func': ast.FunctionDef}),
            ('x', {'y': ast.arg, 'x': ast.arg, 'func': ast.FunctionDef})
        ])

        tree = macropy.core.parse_stmt("""
def func(x, y):
    z = 10
    return x
        """)

        self.assertEqual(scoped.collect(tree), [
            ('\n\ndef func(x, y):\n    z = 10\n    return x', {
                'func': ast.FunctionDef}),
            ('x, y', {'func': ast.FunctionDef}),
            ('x', {'func': ast.FunctionDef}),
            ('y', {'func': ast.FunctionDef}),
            ('\nz = 10', {'y': ast.arg, 'x': ast.arg, 'z': ast.Name,
                          'func': ast.FunctionDef}),
            ('z', {'y': ast.arg, 'x': ast.arg, 'z': ast.Name,
                   'func': ast.FunctionDef}),
            ('10', {'y': ast.arg, 'x': ast.arg, 'z': ast.Name,
                    'func': ast.FunctionDef}),
            ('\nreturn x', {'y': ast.arg, 'x': ast.arg, 'z': ast.Name,
                            'func': ast.FunctionDef}),
            ('x', {'y': ast.arg, 'x': ast.arg, 'z': ast.Name,
                   'func': ast.FunctionDef})
        ])

        tree = macropy.core.parse_stmt("""
class C(A, B):
    z = 10
    printfunction(z)
        """)
        self.assertEqual(scoped.collect(tree), [
            ('\n\nclass C(A, B):\n    z = 10\n    printfunction(z)',
             {'C': ast.ClassDef}),
            ('\nz = 10', {'z': ast.Name}),
            ('z', {'z': ast.Name}),
            ('10', {'z': ast.Name}),
            ('\nprintfunction(z)', {'z': ast.Name}),
            ('printfunction(z)', {'z': ast.Name}),
            ('printfunction', {'z': ast.Name}),
            ('z', {'z': ast.Name})
        ])

        tree = macropy.core.parse_stmt("""
def func(x, y):
    def do_nothing(): pass
    class C(): pass
    printfunction(10)
        """)


        self.assertEqual(scoped.collect(tree), [
            ('\n\ndef func(x, y):\n\n    def do_nothing():\n'
             '        pass\n\n    class C:\n        pass\n'
             '    printfunction(10)', {'func': ast.FunctionDef}),
            ('x, y', {'func': ast.FunctionDef}),
            ('x', {'func': ast.FunctionDef}),
            ('y', {'func': ast.FunctionDef}),
            ('\n\ndef do_nothing():\n    pass',
             {'y': ast.arg, 'x': ast.arg, 'C': ast.ClassDef,
              'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef}),
            ('', {'y': ast.arg, 'x': ast.arg, 'C': ast.ClassDef,
                  'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef}),
            ('\npass', {'y': ast.arg, 'x': ast.arg, 'C': ast.ClassDef,
                        'do_nothing': ast.FunctionDef,
                        'func': ast.FunctionDef}),
            ('\n\nclass C:\n    pass',
             {'y': ast.arg, 'x': ast.arg, 'C': ast.ClassDef,
              'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef}),
            ('\npass',
             {'y': ast.arg, 'x': ast.arg, 'do_nothing': ast.FunctionDef,
              'func': ast.FunctionDef}),
            ('\nprintfunction(10)',
             {'y': ast.arg, 'x': ast.arg, 'C': ast.ClassDef,
              'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef}),
            ('printfunction(10)',
             {'y': ast.arg, 'x': ast.arg, 'C': ast.ClassDef,
              'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef}),
            ('printfunction',
             {'y': ast.arg, 'x': ast.arg, 'C': ast.ClassDef,
              'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef}),
            ('10', {'y': ast.arg, 'x': ast.arg, 'C': ast.ClassDef,
                    'do_nothing': ast.FunctionDef, 'func': ast.FunctionDef})
        ])

        tree = macropy.core.parse_stmt("""
try:
    pass
except Exception as e:
    pass
        """)

        self.assertEqual(scoped.collect(tree), [
            ('\npass', {'e': str})
        ])

        # This one still doesn't work right
        tree = macropy.core.parse_stmt("""
C = 1
class C:
    C
C
        """)
