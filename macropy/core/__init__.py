# -*- coding: utf-8 -*-
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


from . import util, compat


__all__ = ['Literal', 'Captured', 'ast_repr', 'parse_expr', 'parse_stmt',
           'real_repr', 'unparse']


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
    tx = type(x)
    if tx in (int, float):
        return ast.Num(n=x)
    elif tx is bytes:
        return ast.Bytes(s=x)
    elif isinstance(x, str):
        return ast.Str(s=x)
    elif tx is list:
        return ast.List(elts=list(map(ast_repr, x)))
    elif tx is dict:
        return ast.Dict(keys=list(map(ast_repr, x.keys())),
                        values=list(map(ast_repr, x.values())))
    elif tx is set:
        return ast.Set(elts=list(map(ast_repr, x)))
    elif tx is Literal:
        return x.body
    elif tx is Captured:
        return compat.Call(ast.Name(id="Captured"), [x.val, ast_repr(x.name)], [])
    elif tx in (bool, type(None)):
        return ast.NameConstant(value=x)
    elif isinstance(x, ast.AST):
        fields = [ast.keyword(a, ast_repr(b)) for a, b in ast.iter_fields(x)]
        # This hard-codes an expectation that ast classes will be
        # bound to the name `ast`.  There must be a better way.
        return compat.Call(ast.Attribute(
            value=ast.Name(id='ast', ctx=ast.Load()),
            attr=x.__class__.__name__, ctx=ast.Load()), [], fields)

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


INFSTR = "1e" + repr(sys.float_info.max_10_exp + 1)


binop = {
    ast.Add: "+",        ast.Sub: "-",        ast.Mult: "*",
    ast.Div: "/",        ast.Mod: "%",        ast.LShift: "<<",
    ast.RShift: ">>",    ast.BitOr: "|",      ast.BitXor: "^",
    ast.BitAnd: "&",     ast.FloorDiv: "//",  ast.Pow: "**"
}

if compat.PY35:
    binop.update({
        ast.MatMult: "@",
    })

unop = {
    ast.Invert: "~",     ast.Not: "not",     ast.UAdd: "+",   ast.USub: "-"
}
cmpops = {
    ast.Eq: "==",        ast.NotEq: "!=",     ast.Lt: "<",
    ast.LtE: "<=",       ast.Gt: ">",         ast.GtE: ">=",
    ast.Is: "is",        ast.IsNot: "is not", ast.In: "in",
    ast.NotIn: "not in"
}
boolops = {
    ast.And: 'and',     ast.Or: 'or'
}


def else_rec(tree, i):
    if not tree:
        return ""
    if isinstance(tree[0], ast.If):
        return tabs(i) + "elif " + rec(tree[0].test, i) + ":" + \
                rec(tree[0].body, i+1) + else_rec(tree[0].orelse, i)
    return tabs(i) + "else:" + rec(tree, i+1)


trec = {
    # Misc
    type(None):     lambda tree, i: "",
    Literal:        lambda tree, i: "$Literal(%s)" % rec(tree.body, i),
    Captured:       lambda tree, i: "$Captured(%s)" % tree.name,
    list:           lambda tree, i: jmap("", lambda t: rec(t, i), tree),

    ast.Module:     lambda tree, i: jmap("", lambda t: rec(t, i), tree.body),

    #Statements
    ast.Expr:       lambda tree, i: tabs(i) + rec(tree.value, i),
    ast.Import:     lambda tree, i: (tabs(i) + "import " +
                                     jmap(", ", lambda t: rec(t, i), tree.names)),
    ast.ImportFrom: lambda tree, i: (tabs(i) + "from " + ("." * tree.level) +
                                     mix(tree.module) + " import " +
                                     jmap(", ", lambda t: rec(t, i), tree.names)),
    ast.Assign:     lambda tree, i: (tabs(i) +
                                     "".join(rec(t, i) + " = " for t in tree.targets) +
                                     rec(tree.value, i)),
    ast.AugAssign:  lambda tree, i: (tabs(i) + rec(tree.target, i) + " " +
                                     binop[tree.op.__class__] + "= " +
                                     rec(tree.value, i)),
    ast.Return:     lambda tree, i: tabs(i) + "return" + mix(" ", rec(tree.value, i)),
    ast.Pass:       lambda tree, i: tabs(i) + "pass",
    ast.Break:      lambda tree, i: tabs(i) + "break",
    ast.Continue:   lambda tree, i: tabs(i) + "continue",
    ast.Delete:     lambda tree, i: (tabs(i) + "del " +
                                     jmap(", ", lambda t: rec(t, i), tree.targets)),
    ast.Assert:     lambda tree, i: (tabs(i) + "assert " + rec(tree.test, i) +
                                     mix(", ", rec(tree.msg, i))),
    ast.Global:     lambda tree, i: tabs(i) + "global " + ", ".join(tree.names),
    ast.Yield:      lambda tree, i: "(yield " + rec(tree.value, i) + ")",
    ast.YieldFrom:  lambda tree, i: "(yield from " + rec(tree.value, i) + ")",
    ast.ExceptHandler: lambda tree, i: (tabs(i) + "except" +
                                mix(" ", rec(tree.type, i)) +
                                mix(" as ", rec(tree.name, i)) + ":" +
                                rec(tree.body, i+1)),
    ast.For:        lambda tree, i: (tabs(i) + "for " + rec(tree.target, i) +
                                     " in " + rec(tree.iter, i) + ":" +
                                     rec(tree.body, i+1) +
                                     mix(tabs(i), "else:", rec(tree.orelse, i+1))),
    ast.If:         lambda tree, i: (tabs(i) + "if " + rec(tree.test, i) + ":" +
                                     rec(tree.body, i+1) + else_rec(tree.orelse, i)),
    ast.While:      lambda tree, i: (tabs(i) + "while " + rec(tree.test, i) + ":" +
                                     rec(tree.body, i+1) +
                                     mix(tabs(i), "else:", rec(tree.orelse, i+1))),

                                #Expressions Str doesn't properly
                                #handle from __future__ import
                                #unicode_literals
    ast.Str:        lambda tree, i: repr(tree.s),
    ast.Name:       lambda tree, i: str(tree.id),
    ast.Num:        lambda tree, i: (lambda repr_n:
                                    ("(" + repr_n.replace("inf", INFSTR) +
                                     ")" if repr_n.startswith("-")
                                    else repr_n.replace("inf", INFSTR)))(repr(tree.n)),
    ast.List:       lambda tree, i: ("[" +
                                     jmap(", ", lambda t: rec(t, i), tree.elts)
                                     + "]"),
    ast.ListComp:   lambda tree, i: ("[" + rec(tree.elt, i) +
                                     jmap("", lambda t: rec(t, i),
                                          tree.generators) + "]"),
    ast.GeneratorExp: lambda tree, i: ("(" + rec(tree.elt, i) +
                                       jmap("", lambda t: rec(t, i),
                                            tree.generators) + ")"),
    ast.SetComp:    lambda tree, i: ("{" + rec(tree.elt, i) +
                                     jmap("", lambda t: rec(t, i),
                                          tree.generators) + "}"),
    ast.DictComp:   lambda tree, i: ("{" + rec(tree.key, i) + ": " +
                                     rec(tree.value, i) +
                                     jmap("", lambda t: rec(t, i),
                                          tree.generators) + "}"),
    ast.comprehension:  lambda tree, i: (" for " + rec(tree.target, i) +
                                         " in " + rec(tree.iter, i) +
                                         jmap("", lambda x: " if " + rec(x, i),
                                              tree.ifs)),
    ast.IfExp:      lambda tree, i: ("(" + rec(tree.body, i) + " if " +
                                     rec(tree.test, i) + " else " +
                                     rec(tree.orelse, i) + ")"),
    ast.Set:        lambda tree, i: ("{" + jmap(", ", lambda t: rec(t, i),
                                                tree.elts) + "}"),
    ast.Dict:       lambda tree, i: ("{" + jmap(", ", lambda x, y: rec(x, i) +
                                                ":" + rec(y, i),
                                                tree.keys, tree.values) + "}"),
    ast.Tuple:      lambda tree, i: ("(" + jmap(", ", lambda t: rec(t, i),
                                                tree.elts) +
                                     ("," if len(tree.elts) == 1 else "") + ")"),

    ast.UnaryOp:    lambda tree, i: ("(" + unop[tree.op.__class__] +
                                     ("(" + rec(tree.operand, i) + ")"
                                      if (type(tree.op) is ast.USub and
                                          type(tree.operand) is ast.Num)
                                      else " " + rec(tree.operand, i)) +
                                     ")"),

    ast.BinOp:      lambda tree, i: ("(" + rec(tree.left, i) + " " +
                                     binop[tree.op.__class__] + " " +
                                     rec(tree.right, i) + ")"),
    ast.Compare:    lambda tree, i: ("(" + rec(tree.left, i) +
                                     jmap("", lambda op, c:(" " +
                                                            cmpops[op.__class__] +
                                                            " " + rec(c, i)),
                                          tree.ops, tree.comparators) + ")"),
    ast.BoolOp:     lambda tree, i: ("(" + jmap(" " + boolops[tree.op.__class__] + " ",
                                                lambda t: rec(t, i),
                                                tree.values) +
                                     ")"),
    ast.Attribute:  lambda tree, i: (rec(tree.value, i) +
                                     (" " if (isinstance(tree.value, ast.Num) and
                                              isinstance(tree.value.n, int))
                                      else "") + "." + tree.attr),
    ast.Subscript:  lambda tree, i: (rec(tree.value, i) + "[" +
                                     rec(tree.slice, i) + "]"),
    ast.Ellipsis:   lambda tree, i: "...",
    ast.Index:      lambda tree, i: rec(tree.value, i),
    ast.Slice:      lambda tree, i: (rec(tree.lower, i) + ":" +
                                     rec(tree.upper, i) +
                                     mix(":", rec(tree.step, i))),
    ast.ExtSlice:   lambda tree, i: jmap(", ", lambda t: rec(t, i), tree.dims),
    ast.arguments:  lambda tree, i: ", ".join(
                                    list(map(lambda a, d: rec(a, i) +
                                             mix("=", rec(d, i)),
                                             tree.args,
                                             [None] * (len(tree.args) -
                                                       len(tree.defaults)) +
                                             tree.defaults)) +
                                    util.box(mix("*", tree.vararg)) +
                                    util.box(mix("**", tree.kwarg))
                                ),
    ast.keyword:    lambda tree, i: ((tree.arg + "=" if tree.arg else '**') +
                                     rec(tree.value, i)),
    ast.Lambda:     lambda tree, i: ("(lambda" + mix(" ", rec(tree.args, i)) +
                                     ": "+ rec(tree.body, i) + ")"),
    ast.alias:      lambda tree, i: tree.name + mix(" as ", tree.asname),
    str:            lambda tree, i: tree,
    ast.Nonlocal:   lambda tree, i: (tabs(i) + "nonlocal " +
                                     jmap(", ", lambda x: x, tree.names)),
    ast.Raise:      lambda tree, i: (tabs(i) + "raise" +
                                     mix(" ", rec(tree.exc, i)) +
                                     mix(" from ", rec(tree.cause, i))), # See PEP-344 for semantics
    ast.Try:        lambda tree, i: (tabs(i) + "try:" + rec(tree.body, i+1) +
                                     jmap("", lambda t: rec(t,i), tree.handlers) +
                                     mix(tabs(i), "else:", rec(tree.orelse, i+1)) +
                                     mix(tabs(i), "finally:",
                                         rec(tree.finalbody, i+1))),
    ast.ClassDef:   lambda tree, i: ("\n" +
                                "".join(tabs(i) + "@" + rec(dec, i) for dec in tree.decorator_list) +
                                tabs(i) + "class " + tree.name +
                            mix("(", ", ".join(
                                [rec(t, i) for t in tree.bases + tree.keywords] +
                                ["*" + rec(t, i) for t in util.box(tree.starargs)] +
                                ["**" + rec(t, i) for t in util.box(tree.kwargs)]
                            ), ")") + ":" + rec(tree.body, i+1)),
    ast.FunctionDef:lambda tree, i: ("\n" + "".join(tabs(i) + "@" + rec(dec, i)
                                                    for dec in tree.decorator_list) +
                                     tabs(i) + "def " + tree.name + "(" +
                                     rec(tree.args, i) + ")" +
                                     mix(" -> ", rec(tree.returns, i)) +  ":" +
                                     rec(tree.body, i+1)),
    ast.With:       lambda tree, i: (tabs(i) + "with " +
                                     jmap(", ", lambda x: rec(x,i), tree.items) +
                                     ":"  + rec(tree.body, i+1)),
    ast.Bytes:      lambda tree, i: repr(tree.s),
    ast.Starred:    lambda tree, i: "*" + rec(tree.value, i),
    ast.arg:        lambda tree, i: (tree.arg + mix(": ", rec(
        getattr(tree,
                'annotation', None), i))),
    ast.withitem:   lambda tree, i: (rec(tree.context_expr, i) +
                                     mix(" as ", rec(tree.optional_vars, i))),
    ast.arguments:  lambda tree, i: (", ".join(
        list(map(
            lambda a, d: (rec(a, i) + mix("=", rec(d, i))),
            tree.args,
            [None] * (len(tree.args) - len(tree.defaults)) + tree.defaults
        )) + util.box(
            mix("*", rec(tree.vararg, i))) +
        [rec(a, i) + "=" + rec(d, i)
         for a, d in zip(tree.kwonlyargs, tree.kw_defaults)] +
        util.box(mix("**", rec(tree.kwarg, i))))),
    ast.Call:       lambda tree, i: (rec(tree.func, i) + "(" +
                                ", ".join(
                                    [rec(t, i) for t in tree.args] +
                                    [rec(t, i) for t in tree.keywords] +
                                    util.box(mix("*", rec(tree.starargs, i))) +
                                    util.box(mix("**", rec(tree.kwargs, i)))
                                ) + ")") ,
}

if compat.PY34:
    trec.update({
        ast.NameConstant: lambda tree, i: str(tree.value),
        })

if compat.PY35:
    trec.update({
        ast.AsyncFor: lambda tree, i: (tabs(i) + "async for " + rec(tree.target, i) +
                                  " in " + rec(tree.iter, i) + ":" +
                                  rec(tree.body, i+1) +
                                  mix(tabs(i), "else:", rec(tree.orelse, i+1))),
        ast.AsyncFunctionDef: lambda tree, i: ("\n" +
                                          "".join(tabs(i) + "@" + rec(dec, i)
                                                  for dec in tree.decorator_list) +
                                          tabs(i) + "async def " + tree.name + "(" +
                                          rec(tree.args, i) + ")" +
                                          mix(" -> ", rec(tree.returns, i)) +  ":" +
                                          rec(tree.body, i+1)),
        ast.AsyncWith: lambda tree, i: (tabs(i) + "async with " +
                                   jmap(", ", lambda x: rec(x,i), tree.items) +
                                   ":"  + rec(tree.body, i+1)),
        ast.Await: lambda tree, i: "(await " + rec(tree.value, i) + ")",
        ast.Call: lambda tree, i: (rec(tree.func, i) + "(" +
                                ", ".join(
                                    [rec(t, i) for t in tree.args] +
                                    [rec(t, i) for t in tree.keywords]) +
                                ")"),
        ast.ClassDef: lambda tree, i: ("\n" +
                                  "".join(tabs(i) + "@" + rec(dec, i)
                                          for dec in tree.decorator_list) +
                                  tabs(i) + "class " + tree.name +
                                  mix("(",
                                      ", ".join([rec(t, i)
                                                 for t in (tree.bases +
                                                           tree.keywords)]),
                                      ")") + ":" + rec(tree.body, i+1)),
        # See https://greentreesnakes.readthedocs.io/en/latest/nodes.html#Dict
        ast.Dict: lambda tree, i: ("{" + jmap(", ", lambda k, v: (((rec(k, i) + ":")
                                                        if k is not None
                                                        else "**")
                                                        + rec(v, i)),
                                         tree.keys, tree.values) + "}"),
    })

if compat.PY36:
    trec.update({
        ast.AnnAssign: lambda tree, i: (tabs(i) +
                                   (rec(tree.target, i)
                                    if tree.simple else
                                    "(" + rec(tree.target, i) + ")") +
                                   ": " + rec(tree.annotation, i) +
                                   ((" = " + rec(tree.value, i) if tree.value
                                     else ""))),
        ast.comprehension: lambda tree, i: ((" async" if getattr(tree, 'is_async',
                                                            False)
                                        else "") + " for " + rec(tree.target, i) +
                                       " in " + rec(tree.iter, i) +
                                       jmap("", lambda x: " if " + rec(x, i),
                                            tree.ifs))
    })

if compat.HAS_FSTRING:
    trec.update({
        ast.FormattedValue: lambda tree, i: ("{" +  rec(tree.value, i) +
                                        {-1: "", 115: "!s", 114: "!r",
                                         115: "!a"}[tree.conversion] +
                                        ((":" + tree.format_spec.values[0].s)
                                         if tree.format_spec else "") +
                                        "}"),
        ast.JoinedStr: lambda tree, i: "f" + repr("".join(v.s
            if isinstance(v, ast.Str) else rec(v, i) for v in tree.values))
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


def _ast_leftovers():
    """Return a set of the AST nodes not yet covered by unparse"""
    ast_classes = {v for v in vars(ast).values()
                   if isinstance(v, type)
                   if issubclass(v, ast.AST)
                   if v is not ast.AST}

    expr_ctxs = {ast.Load, ast.Store, ast.AugStore, ast.AugLoad, ast.Param}
    top_nodes = {ast.Module, ast.Expression, ast.Interactive}
    jython = {ast.Suite}
    optimizations = {ast.Del}
    if compat.PY36:
        optimizations.add(ast.Constant)
    if compat.PYPY:
        optimizations.add(ast.Const)

    sups = set()
    sups.update(*{v.__bases__ for v in ast_classes})

    terms = ast_classes.difference(sups, expr_ctxs, top_nodes, jython,
                                   optimizations)

    remainder = {v for v in terms
                 if v not in trec
                 if v not in binop
                 if v not in unop
                 if v not in cmpops
                 if v not in boolops}
    return remainder
