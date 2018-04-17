# -*- coding: utf-8 -*-
import unittest

import macropy.core
import macropy.core.compat as compat


def convert(code):
    " string -> ast -> string "
    return macropy.core.unparse(macropy.core.parse_stmt(code))


class Tests(unittest.TestCase):

    def convert_test(self, code):
        # check if unparsing the ast of code yields the same source
        self.assertEqual(code.rstrip(), convert(code))

    def test_expr(self):
        self.assertEqual(convert("1 +2 / a"), "\n(1 + (2 / a))")

    def test_stmts(self):
        test = """
import foo
from foo import bar
foo = something
bar += 4
return
pass
break
continue
del a, b, c
assert foo, bar
del foo
global foo, bar, baz
(yield foo)
print('hello', 'world')
nonlocal foo, bar, baz"""
        self.convert_test(test)

    def test_Exec(self):
        self.convert_test("""
exec('foo')
exec('foo', bar)
exec('foo', bar, {})""")

    def test_Raise(self):
        self.convert_test("""
raise
raise Exception(e)
raise Exception from init_arg""")

    def test_Try(self):
        self.convert_test("""
try:
    foo
except:
    pass
try:
    foo
except Exeption as name:
    bar
except Exception:
    123
except:
    pass
else:
    baz
finally:
    foo.close()
try:
    foo
finally:
    foo.close()""")

    def test_ClassDef(self):
        self.convert_test("""

@decorator
@decorator2
class Foo(bar, baz):
    pass

class Bar(metaclass=Meta):
    pass""")

    def test_FunctionDef(self):
        # also tests the arguments object
        self.convert_test("""

@decorator
@decorator2
def foo():
    bar

def foo(arg, arg2, kw=5, *args, kwonly=4, **kwargs):
    pass""")

    def test_For(self):
        self.convert_test("""
for a in b:
    pass
else:
    bar
for a in b:
    pass""")

    def test_If(self):
        self.convert_test("""
if foo:
    if foo:
        pass
    else:
        pass
if foo:
    pass
elif c:
    if foo:
        pass
    elif a:
        pass
    elif b:
        pass
    else:
        pass
""")

    def test_While(self):
        self.convert_test("""
while a:
    pass
else:
    pass
while a:
    pass""")

    def test_With(self):
        self.convert_test("""
with a as b:
    c""")

    def test_datatypes(self):
        self.convert_test("""
{1, 2, 3, 4}
{1:2, 5:8}
(1, 2, 3)
""")
        self.convert_test("\n[1, 5.0, [(-(6))]]")
        self.convert_test("\n'abcd'")

    def test_comprehension(self):
        self.convert_test("""
(5 if foo else bar)
(x for x in abc)
(x for x in abc if foo)
[x for x in abc if foo]
{x for x in abc if foo}
{x: y for x in abc if foo}
""")

    def test_unaryop(self):
        self.convert_test("""
(not foo)
(~ 9)
(+ 1)
""")

    def test_bnops(self):
        self.convert_test("\n(1 >> (2 | 3))")
        self.convert_test("\n(a >= b)")

    def test_misc(self):
        self.convert_test("\na.attr") # Attribute
        if compat.PY35:
            self.convert_test("""
f()
f(a, *b, k=8, e=9, **c)""") # Call
        else:
            # Py3.4 version of ast.Call unparser doesn't deal with
            # starargs before keywords
            self.convert_test("""
f()
f(a, k=8, e=9, *b, **c)""") # Call

        #self.convert_test("\n...") # Ellipsis
        self.convert_test("""
a[1]
a[1:2]
a[2:3:4]
a[(1,)]""") # subscript, Index, Slice, extslice
        self.convert_test("""
(lambda k, f, a=6, *c, **kw: 7)
(lambda: 7)
""")

    def test_ann_assign(self):
        if not compat.PY36:
            return
        self.convert_test("""
a: Int
(b.c): Bool = False
(d[1]): Int
""")

    def test_dict_star_star_expand(self):
        if not compat.PY35:
            return
        self.convert_test("""
{'a':1, **d}""")

    def test_joined_str(self):
        if not compat.HAS_FSTRING:
            return
        self.convert_test("""
f'bar {grande!r:foo}   zoo'
""")

    def test_async(self):
        if not compat.PY35:
            return
        # do not remove the empty line in the string, or the test will
        # not pass
        self.convert_test("""

async def foo(a: Int):
    async for foo in aiter:
        pass
    async with foo as bar:
        pass
    (await future)
""")

    def test_async_comprehensions(self):
        if not compat.PY36:
            return
        self.convert_test("""

async def foo():
    result = [i async for i in aiter() if (i % 2)]
    result = [(await fun()) for fun in funcs if (await condition())]
""")

    def test_leftovers(self):
        self.assertEqual(macropy.core._ast_leftovers(), set())
