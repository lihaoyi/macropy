"""
This package contains all the infrastructure required for MacroPy itself to
function, separate from the individual implementation of cool macros. It
bundles the `quotes` macro as it is a fundamental tool in the macro creation
process.

This file itself contains the basic operations necessary to transform between
code in various forms: Source, ASTs, and Values. These operations wrap more
primitive forms (e.g. in the ast module) which should not be used directly.

This map maps out how to convert from form to form:

                     parse_stmt
       ____________  parse_expr  ____________
      |            |----------->|            |
      |   Source   |            |    AST     |
      |____________|<-----------|____________|
          ^     |      unparse    |        ^
          |     |     exact_src   | eval   | ast_repr
          |     |                 |        |
real_repr |     |    eval        _v________|_
          |     --------------->|            |
          |                     |   Value    |
          ----------------------|____________|
"""
import ast
import sys
from .util import *
from six import PY3, string_types
__all__ = ['Literal', 'Captured', 'ast_repr', 'parse_expr', 'parse_stmt', 'real_repr', 'unparse', 'box']

class Literal(object):
    """Used to wrap sections of an AST which must remain intact when
    `ast_repr`ed or `real_repr`ed."""
    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return unparse(self.body)


class Captured(object):
    def __init__(self, val, name):
        self.val = val
        self.name = name


def ast_repr(x):
    """Similar to repr(), but returns an AST instead of a String, which when
    evaluated will return the given value."""
    if type(x) in (int, float):      return ast.Num(n=x)
    elif PY3 and type(x) is bytes:   return ast.Bytes(s=x)
    elif isinstance(x,string_types): return ast.Str(s=x)
    elif type(x) is list:            return ast.List(elts=list(map(ast_repr, x)))
    elif type(x) is dict:            return ast.Dict(keys=list(map(ast_repr, x.keys())), values=list(map(ast_repr, x.values())))
    elif type(x) is set:             return ast.Set(elts=list(map(ast_repr, x)))
    elif type(x) is Literal:         return x.body
    elif type(x) is Captured:
        return ast.Call(
            ast.Name(id="Captured"),
            [x.val, ast_repr(x.name)], [], None, None
        )
    elif type(x) in (bool, type(None)):
        if sys.version_info >= (3, 4):  return ast.NameConstant(value=x)
        else:                           return ast.Name(id=str(x))
    elif isinstance(x, ast.AST):
        fields = [ast.keyword(a, ast_repr(b)) for a, b in ast.iter_fields(x)]
        return ast.Call(
            ast.Name(id=x.__class__.__name__),
            [], fields, None, None
        )
    raise Exception("Don't know how to ast_repr this: ", x)

def parse_expr(x):
    """Parses a string into an `expr` AST"""
    return ast.parse(x).body[0].value


def parse_stmt(x):
    """Parses a string into an `stmt` AST"""
    return ast.parse(x).body


def real_repr(thing):
    """Converts the given value into a string which when evaluated will
    return the value. This one is smart enough to take care of ASTs"""
    if isinstance(thing, ast.AST):
        fields = [real_repr(b) for a, b in ast.iter_fields(thing)]
        return '%s(%s)' % (thing.__class__.__name__, ', '.join(fields))

    elif isinstance(thing, list):
        return '[%s]' % ', '.join(map(real_repr, thing))
    return repr(thing)

from ast import *
INFSTR = "1e" + repr(sys.float_info.max_10_exp + 1)


binop = {
    Add: "+",        Sub: "-",        Mult: "*",
    Div: "/",        Mod: "%",        LShift: "<<",
    RShift: ">>",    BitOr: "|",      BitXor: "^",
    BitAnd: "&",     FloorDiv: "//",  Pow: "**"
}
unop = {
    Invert: "~",     Not: "not",     UAdd: "+",   USub: "-"
}
cmpops = {
    Eq: "==",        NotEq: "!=",     Lt: "<",
    LtE: "<=",       Gt: ">",         GtE: ">=",
    Is: "is",        IsNot: "is not", In: "in",
    NotIn: "not in"
}
boolops = {
    And: 'and',     Or: 'or'
}

def else_rec(tree, i):
    if not tree: 
        return ""
    if isinstance(tree[0], If):
        return tabs(i) + "elif " + rec(tree[0].test, i) + ":" + \
                rec(tree[0].body, i+1) + else_rec(tree[0].orelse, i)
    return tabs(i) + "else:" + rec(tree, i+1)
    

trec = {
    #Misc
    type(None): lambda tree, i: "",
    Literal:    lambda tree, i: "$Literal(%s)" % rec(tree.body, i),
    Captured:    lambda tree, i: "$Captured(%s)" % tree.name,
    list:       lambda tree, i: jmap("", lambda t: rec(t, i), tree),

    Module:     lambda tree, i: jmap("", lambda t: rec(t, i), tree.body),

    #Statements
    Expr:       lambda tree, i: tabs(i) + rec(tree.value, i),
    Import:     lambda tree, i: tabs(i) + "import " + jmap(", ", lambda t: rec(t, i), tree.names),
    ImportFrom: lambda tree, i: tabs(i) + "from " + ("." * tree.level) + mix(tree.module) +
                                " import " + jmap(", ", lambda t: rec(t, i), tree.names),
    Assign:     lambda tree, i: tabs(i) + "".join(rec(t, i) + " = " for t in tree.targets) + rec(tree.value, i),
    AugAssign:  lambda tree, i: tabs(i) + rec(tree.target, i) + " " + binop[tree.op.__class__] + "= " + rec(tree.value, i),
    Return:     lambda tree, i: tabs(i) + "return" + mix(" ", rec(tree.value, i)),
    Pass:       lambda tree, i: tabs(i) + "pass",
    Break:      lambda tree, i: tabs(i) + "break",
    Continue:   lambda tree, i: tabs(i) + "continue",
    Delete:     lambda tree, i: tabs(i) + "del " + jmap(", ", lambda t: rec(t, i), tree.targets),
    Assert:     lambda tree, i: tabs(i) + "assert " + rec(tree.test, i) + mix(", ", rec(tree.msg, i)),
    Global:     lambda tree, i: tabs(i) + "global " + ", ".join(tree.names),
    Yield:      lambda tree, i: "(yield " + rec(tree.value, i) + ")",
    ExceptHandler: lambda tree, i: tabs(i) + "except" +
                                mix(" ", rec(tree.type, i)) +
                                mix(" as ", rec(tree.name, i)) + ":" +
                                rec(tree.body, i+1),
    For:        lambda tree, i: tabs(i) + "for " + rec(tree.target, i) + " in " +
                                rec(tree.iter, i) + ":" + rec(tree.body, i+1) +
                                mix(tabs(i), "else:", rec(tree.orelse, i+1)),
    If:         lambda tree, i: tabs(i) + "if " + rec(tree.test, i) + ":" + rec(tree.body, i+1) +
                                else_rec(tree.orelse, i),
    While:      lambda tree, i: tabs(i) + "while " + rec(tree.test, i) + ":" + rec(tree.body, i+1) +
                                mix(tabs(i), "else:", rec(tree.orelse, i+1)),

                                #Expressions
                                #Str doesn't properly handle from __future__ import unicode_literals
    Str:        lambda tree, i: repr(tree.s),
    Name:       lambda tree, i: str(tree.id),
    Num:        lambda tree, i: (lambda repr_n:
                                    "(" + repr_n.replace("inf", INFSTR) + ")"
                                    if repr_n.startswith("-")
                                    else repr_n.replace("inf", INFSTR)
                                )(repr(tree.n)),
    List:       lambda tree, i: "[" + jmap(", ", lambda t: rec(t, i), tree.elts) + "]",
    ListComp:   lambda tree, i: "[" + rec(tree.elt, i) + jmap("", lambda t: rec(t, i), tree.generators) + "]",
    GeneratorExp: lambda tree, i: "(" + rec(tree.elt, i) + jmap("", lambda t: rec(t, i), tree.generators) + ")",
    SetComp:    lambda tree, i: "{" + rec(tree.elt, i) + jmap("", lambda t: rec(t, i), tree.generators) + "}",
    DictComp:   lambda tree, i: "{" + rec(tree.key, i) + ": " + rec(tree.value, i) + jmap("", lambda t: rec(t, i), tree.generators) + "}",
    comprehension:  lambda tree, i: " for " + rec(tree.target, i) + " in " + rec(tree.iter, i) + jmap("", lambda x: " if " + rec(x, i), tree.ifs),
    IfExp:      lambda tree, i: "(" + rec(tree.body, i) + " if " + rec(tree.test, i) + " else " + rec(tree.orelse, i) + ")",
    Set:        lambda tree, i: "{" + jmap(", ", lambda t: rec(t, i), tree.elts) + "}",
    Dict:       lambda tree, i: "{" + jmap(", ", lambda x, y: rec(x, i) + ":" + rec(y, i), tree.keys, tree.values) + "}",
    Tuple:      lambda tree, i: "(" + jmap(", ", lambda t: rec(t, i), tree.elts) + ("," if len(tree.elts) == 1 else "") + ")",
    UnaryOp:    lambda tree, i: "(" + unop[tree.op.__class__] +
                                ("(" + rec(tree.operand, i) + ")"
                                if type(tree.op) is USub and type(tree.operand) is Num
                                else " " + rec(tree.operand, i)) + ")",
    BinOp:      lambda tree, i: "(" + rec(tree.left, i) + " " + binop[tree.op.__class__] + " " + rec(tree.right, i) + ")",
    Compare:    lambda tree, i: "(" + rec(tree.left, i) + jmap("", lambda op, c: " " + cmpops[op.__class__] + " " + rec(c, i), tree.ops, tree.comparators) + ")",
    BoolOp:     lambda tree, i: "(" + jmap(" " + boolops[tree.op.__class__] + " ", lambda t: rec(t, i), tree.values) + ")",
    Attribute:  lambda tree, i: rec(tree.value, i) + (" " if isinstance(tree.value, Num) and isinstance(tree.value.n, int) else "") + "." + tree.attr,
    Call:       lambda tree, i: rec(tree.func, i) + "(" +
                                ", ".join(
                                    [rec(t, i) for t in tree.args] +
                                    [rec(t, i) for t in tree.keywords] +
                                    box(mix("*", rec(tree.starargs, i))) +
                                    box(mix("**", rec(tree.kwargs, i)))
                                ) + ")",
    Subscript:  lambda tree, i: rec(tree.value, i) + "[" + rec(tree.slice, i) + "]",
    Ellipsis:   lambda tree, i: "...",
    Index:      lambda tree, i: rec(tree.value, i),
    Slice:      lambda tree, i: rec(tree.lower, i) + ":" + rec(tree.upper, i) + mix(":", rec(tree.step, i)),
    ExtSlice:   lambda tree, i: jmap(", ", lambda t: rec(t, i), tree.dims),
    arguments:  lambda tree, i: ", ".join(
                                    list(map(lambda a, d: rec(a, i) + mix("=", rec(d, i)),
                                        tree.args,
                                        [None] * (len(tree.args) - len(tree.defaults)) + tree.defaults
                                    )) +
                                    box(mix("*", tree.vararg)) +
                                    box(mix("**", tree.kwarg))
                                ),
    keyword:    lambda tree, i: tree.arg + "=" + rec(tree.value, i),
    Lambda:     lambda tree, i: "(lambda" + mix(" ", rec(tree.args, i)) + ": "+ rec(tree.body, i) + ")",
    alias:      lambda tree, i: tree.name + mix(" as ", tree.asname),
    str:        lambda tree, i: tree
}

if PY3:
    trec.update({
        Nonlocal:   lambda tree, i: tabs(i) + "nonlocal " + jmap(", ", lambda x: x, tree.names),
        YieldFrom:  lambda tree, i: "(yield from " + rec(tree.value, i) + ")",
        Raise:      lambda tree, i: tabs(i) + "raise" + 
                            mix(" ", rec(tree.exc, i)) +
                            mix(" from ", rec(tree.cause, i)), # See PEP-344 for semantics
        Try:        lambda tree, i: tabs(i) + "try:" + rec(tree.body, i+1) +
                            jmap("", lambda t: rec(t,i), tree.handlers) +
                            mix(tabs(i), "else:", rec(tree.orelse, i+1)) +
                            mix(tabs(i), "finally:", rec(tree.finalbody, i+1)),
        ClassDef:   lambda tree, i: "\n" + "".join(tabs(i) + "@" + rec(dec, i) for dec in tree.decorator_list) +
                            tabs(i) + "class " + tree.name +
                            mix("(", ", ".join(
                                [rec(t, i) for t in tree.bases + tree.keywords] +
                                ["*" + rec(t, i) for t in box(tree.starargs)] +
                                ["**" + rec(t, i) for t in box(tree.kwargs)]
                            ), ")") + ":" + rec(tree.body, i+1),
        FunctionDef:lambda tree, i: "\n" + "".join(tabs(i) + "@" + rec(dec, i) for dec in tree.decorator_list) +
                                    tabs(i) + "def " + tree.name + "(" + rec(tree.args, i) + ")" + 
                                    mix(" -> ", rec(tree.returns, i)) +  ":" + rec(tree.body, i+1),
        With:       lambda tree, i: tabs(i) + "with " + jmap(", ", lambda x: rec(x,i), tree.items) + ":" + 
                                    rec(tree.body, i+1),
        Bytes:      lambda tree, i: repr(tree.s),
        Starred:    lambda tree, i: "*" + rec(tree.value),
        arg:        lambda tree, i: tree.arg + mix(":", tree.annotation),
        withitem:   lambda tree, i: rec(tree.context_expr, i) + mix(" as ", rec(tree.optional_vars, i)),
        arguments:  lambda tree, i: ", ".join(
                                        list(map(lambda a, d: rec(a, i) + mix("=", rec(d, i)),
                                            tree.args,
                                            [None] * (len(tree.args) - len(tree.defaults)) + tree.defaults
                                        )) +
                                        box(mix("*", rec(tree.vararg, i))) +
                                        # TODO:
                                        #[rec(arg, i) + "=" + rec(d, i) for a, d in zip(tree.kwonlyargs, tree.kw_defaults)] +
                                        box(mix("**", rec(tree.kwarg, i)))
                                    ),
    })
    if sys.version_info >= (3, 4):
        trec[NameConstant] = lambda tree, i: str(tree.value)
else:
    trec.update({
        Exec:       lambda tree, i: tabs(i) + "exec " + rec(tree.body, i) +
                                    mix(" in ", rec(tree.globals, i)) +
                                    mix(", ", rec(tree.locals, i)),
        Print:      lambda tree, i: tabs(i) + "print " +
                                    ", ".join(box(mix(">>", rec(tree.dest, i))) + [rec(t, i) for t in tree.values]) +
                                    ("," if not tree.nl else ""),
        Raise:      lambda tree, i: tabs(i) + "raise" + 
                                    mix(" ", rec(tree.type, i)) +
                                    mix(", ", rec(tree.inst, i)) +
                                    mix(", ", rec(tree.tback, i)),
        TryExcept:  lambda tree, i: tabs(i) + "try:" + rec(tree.body, i+1) +
                                    jmap("", lambda t: rec(t, i), tree.handlers) +
                                    mix(tabs(i), "else:", rec(tree.orelse, i+1)),
        TryFinally: lambda tree, i: (rec(tree.body, i)
                                    if len(tree.body) == 1 and isinstance(tree.body[0], ast.TryExcept)
                                    else tabs(i) + "try:" + rec(tree.body, i+1)) +
                                    tabs(i) + "finally:" + rec(tree.finalbody, i+1),
        ClassDef:   lambda tree, i: "\n" + "".join(tabs(i) + "@" + rec(dec, i) for dec in tree.decorator_list) +
                                    tabs(i) + "class " + tree.name +
                                    mix("(", jmap(", ", lambda t: rec(t, i), tree.bases), ")") + ":" +
                                    rec(tree.body, i+1),
        FunctionDef:lambda tree, i: "\n" + "".join(tabs(i) + "@" + rec(dec, i) for dec in tree.decorator_list) +
                                    tabs(i) + "def " + tree.name + "(" + rec(tree.args, i) + "):" + rec(tree.body, i+1),
        With:       lambda tree, i: tabs(i) + "with " + rec(tree.context_expr, i) +
                                    mix(" as ", rec(tree.optional_vars, i)) + ":" +
                                    rec(tree.body, i+1),
        Repr:       lambda tree, i: "`" + rec(tree.value) + "`",
        arguments:  lambda tree, i: ", ".join(
                                        list(map(lambda a, d: rec(a, i) + mix("=", rec(d, i)),
                                            tree.args,
                                            [None] * (len(tree.args) - len(tree.defaults)) + tree.defaults
                                        )) +
                                        box(mix("*", tree.vararg)) +
                                        box(mix("**", tree.kwarg))
                                    ),
    })

def mix(*x):
    """Join everything together if none of them are empty"""
    return "".join(x) if all(x) else ""

def rec(tree, i):
    """Recurse with same indentation"""
    return trec[tree.__class__](tree, i)

def jmap(s, f, *l):
    """Shorthand for the join+map operation"""
    return s.join(map(f, *l))

def tabs(i): 
    return "\n" + "    "*i

def unparse(tree):
    """Converts an AST back into the source code from whence it came!"""
    return trec[tree.__class__](tree, 0)

