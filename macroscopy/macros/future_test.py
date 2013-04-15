import unittest

from macroscopy.core.macros import *
from macroscopy.core.lift import *
from macroscopy.macros.string_interp import *


def Tests(unittest.TestCase):
    def test_adt(self):
        @adt
        def Call(ast.expr):
            func, args, keywords, starargs, kwargs

    def test_matching(self):
        with ast.Call(x, y, ast.Call(a, b)) as x:
            pass

def adt(x): return x


@adt
def AST():
    def operator():
        def Add(): pass
        def BitAnd(): pass
        def BitOr(): pass
        def BitXor(): pass
        def Div(): pass
        def FloorDiv(): pass
        def LShift(): pass
        def Mod(): pass
        def Mult(id, ctx): pass
        def Pow(): pass
        def RShift(): pass
        def Sub(): pass
    def alias(name, asname): pass
    def boolop():
        def And(): pass
        def Or(): pass
    def arguments(args, varargs, kwarg, defaults): pass
    def stmt(lineno, col_offset):
        def Assert(test, msg): pass
        def Assign(targets, value): pass
        def AugAssign(target, op, value): pass
        def Break(): pass
        def defDef(name, bases, body, decorator_list): pass
        def Continue(): pass
        def Delete(targets): pass
        def Exec(body, globals, locals): pass
        def Expr(value): pass
        def For(target, iter, body, orelse): pass
        def FunctionDef(name, args, body, decorator_list): pass
        def Global(names): pass
        def If(test, body, orelse): pass
        def Import(names): pass
        def ImportFrom(module, names, level): pass
        def Pass(): pass
        def Print(dest, values, nl): pass
        def Raise(type, inst, tback): pass
        def Return(value): pass
        def TryExcept(body, handler, orelse): pass
        def TryFinally(body, finalbody): pass
        def While(test, body, orelse): pass
        def With(context_expr, optional_vars, body): pass
    def expr(lineno, col_offset):
        def Attribute(value, attr, ctx): pass
        def BinOp(left, op, right): pass
        def BoolOp(op, values): pass
        def Call(func, args, keywords, starargs, kwargs): pass
        def Compare(left, op, comparators): pass
        def Dict(keys, values): pass
        def DictComp(key, value, generators): pass
        def GeneratorExp(elt, generators): pass
        def IfExp(test, body, orelse): pass
        def Lambda(args, body): pass
        def List(elts, ctx): pass
        def ListComp(elts, generators): pass
        def Name(id, ctx): pass
        def Num(n): pass
        def Repr(value): pass
        def Set(elts): pass
        def SetComp(elt, generators): pass
        def Str(s): pass
        def Subscript(value, slice, ctx): pass
        def Tuple(elts, ctx): pass
        def UnaryOp(op, operand): pass
        def Yield(value):
    def expr_context():
        def AugLoad(): pass
        def AugStore(): pass
        def Del(): pass
        def Load(): pass
        def Param(): pass
        def Store(): pass
    def cmpop():
        def Eq(): pass
        def Gt(): pass
        def GtE(): pass
        def In(): pass
        def Is(): pass
        def IsNot(): pass
        def Lt(): pass
        def LtE(): pass
        def NotEq(): pass
        def NotIn():pass
    def comprehension(target, iter, ifs): pass
    def slice():
        def Ellipsis(): pass
        def ExtSlice(dims): pass
        def Index(value): pass
        def Slice(lower, upper, step): pass
    def excepthandler(lineno, col_offset):
        def ExceptHandler(type, name, body): pass
    def mod():
        def Expression(body): pass
        def Interactive(body): pass
        def Module(body): pass
        def Suite(body): pass
    def unaryop():
        def Invert(): pass
        def Not(): pass
        def UAdd(): pass
        def USub(): pass
    def keyword(arg, value): pass