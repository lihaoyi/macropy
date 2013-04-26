import unittest

from macropy.core.macros import *
from macropy.core.lift import *
from macropy.macros.string_interp import *

class Tests(unittest.TestCase):
    def test_matching(self):
        pass

class Foo(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

x1 = 10
y1 = 4
if Foo(x=(x1 + 5), y=(y1, 5)) << foo1:

if s%"i am a %{cow} hear me %{moo}" << String:
    print cow
    print moo
if match%("i am a ", cow, "hear me", moo) << string:
    ...
if match("i am a ", cow, " hear me", u%repeat(" moo", 5)) << string:
    i am a cow hear me moo moo moo

macro%(..., ...)

a = Var()
b = Var()


def handleFoo(foo):
    with matcher:
        if Foo(x, Bar(y)) << foo:
            ...
        if Bar(y) << foo:
            ...
    matcher%(Foo(a, b) << thing)
    return a + b

def adt(x): return x

match = ()
unknown = ()

match% IfExp(test=test, body=Str(s="wtf"), orelse=Num(n=n)) ** unknown

assert type(unknown) is IfExp
test = unknown.test
assert type(unknown.body) is Str
assert unknown.body.s == "wtf"
assert type(unknown.orelse) is Num
n = unknown.orelse.n


server = do
    conn <- acceptConn
    handleConn conn


def Maybe():
    def Just(x):
    def Nothing():

monadic%[a + b for a in Just(x) for b in Nothing()] # --> Nothing
monadic%[a + b for a in Just(x) for b in Just(y)] # --> Just(x + y)


LINQ

sql%[a.x for a in database if a.x > 10] # -> SELECT 'x' FROM 'a' IF x > 10

[a + b for a in [1,2,3] for b in [1,2,3]]

with do as result:
    a << [1, 2, 3]
    b << [1, 2, 3]
    a + b

# [2,3,4,3,4,5,4,5,6]

with do:
    with do as replicateM:
        numtimes = 10
        with do as body:
            conn << acceptConn
            handleConn(conn)
= replicateM 10 (do
            conn <- acceptConn
            handleConn conn)
    

assert%(a == 2)   # failure: a == 2


class alias:
    @auto
    def __init__(name, asname): pass

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
        def Yield(value): pass
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
        def Ndot(): pass
        def UAdd(): pass
        def USub(): pass
    def keyword(arg, value): pass


