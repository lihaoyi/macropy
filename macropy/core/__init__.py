"""
This file contains the basic operations necessary to transform between
code in various forms: Source, ASTs, and Values. These operations wrap
more primitive forms (e.g. in the ast module) which should not be used
directly.

This map maps out how to convert from form to form:

                     parse_stmt
       ____________  parse_expr  ____________
      |            |----------->|            |
      |   Source   |            |    AST     |
      |____________|<-----------|____________|
          ^     |   unparse_ast   |        ^
          |     |                 | eval   | ast_repr
          |     |                 |        |
real_repr |     |    eval        _v________|_
          |     --------------->|            |
          |                     |   Value    |
          ----------------------|____________|
"""
import ast
import sys


class Literal(object):
    """Used to wrap sections of an AST which must remain intact when
    `ast_repr`ed or `real_repr`ed."""
    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return unparse_ast(self.body)

def ast_repr(x):
    """Similar to repr(), but returns an AST instead of a String, which when
    evaluated will return the given value."""
    if type(x) in (int, float): return ast.Num(n=x)
    elif type(x) is str:        return ast.Str(s=x)
    elif type(x) is list:       return ast.List(elts=map(ast_repr, x))
    elif type(x) is dict:       return ast.Dict(keys=map(ast_repr, x.keys()), values=map(ast_repr, x.values()))
    elif type(x) is set:        return ast.Set(elts=map(ast_repr, x))
    elif type(x) is Literal:    return x.body
    elif x is None:             return ast.Name(id="None")
    elif isinstance(x, ast.AST):
        fields = [ast.keyword(a, ast_repr(b)) for a, b in ast.iter_fields(x)]
        return ast.Call(
            func = ast.Name(id=x.__class__.__name__),
            args = [],
            keywords = fields,
            starargs = None,
            kwargs = None
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
def unparse_ast(tree):
    """Converts an AST back into the source code from whence it came!"""
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

    def trec(tree, indent):
        def box(x):
            "None | T => [T]"
            return [x] if x else []

        def mix(*x):
            """Join everything together if none of them are empty"""
            return "".join(x) if all(x) else ""

        def rec(tree):
            """Recurse with same indentation"""
            return trec(tree, indent)
        def irec(tree):
            """Recurse with additional indentation"""
            return trec(tree, indent+1)

        tabs = "\n" + "    "*indent
        def jmap(s, f, *l):
            """Shorthand for the join+map operation"""
            return s.join(map(f, *l))

        type_dict = {
            #Misc
            type(None): lambda: "",
            list:       lambda: jmap("", rec, tree),

            Module:     lambda: jmap("", rec, tree.body),

            #Statements
            Expr:       lambda: tabs + rec(tree.value),
            Import:     lambda: tabs + "import " + jmap(", ", rec, tree.names),
            ImportFrom: lambda: tabs + "from " + ("." * tree.level) + mix(tree.module) +
                                " import " + jmap(", ", rec, tree.names),
            Assign:     lambda: tabs + "".join(rec(t) + " = " for t in tree.targets) + rec(tree.value),
            AugAssign:  lambda: tabs + rec(tree.target) + " " + binop[tree.op.__class__] + "= " + rec(tree.value),
            Return:     lambda: tabs + "return " + mix(tree.value),
            Pass:       lambda: tabs + "pass",
            Break:      lambda: tabs + "break",
            Continue:   lambda: tabs + "continue",
            Delete:     lambda: tabs + "del " + jmap(", ", rec, tree.targets),
            Assert:     lambda: tabs + "assert " + rec(tree.test) + mix(", ", rec(tree.msg)),
            Exec:       lambda: tabs + "exec " + rec(tree.body) +
                                mix(" in ", rec(tree.globals)) +
                                mix(", ", rec(tree.locals)),
            Print:      lambda: tabs + "print " +
                                ", ".join(box(mix(">>", rec(tree.dest))) + map(rec, tree.values)) +
                                ("," if not tree.nl else ""),
            Global:     lambda: tabs + "global " + jmap(", ", rec, tree.names),
            Yield:      lambda: "(yield " + rec(tree.value) + ")",
            Raise:      lambda: tabs + "raise " + rec(tree.type) +
                                mix(", ", rec(tree.inst)) +
                                mix(", ", rec(tree.tback)),
            TryExcept:  lambda: tabs + "try:" + irec(tree.body) +
                                jmap("", rec, tree.handlers) +
                                mix(tabs, "else:", irec(tree.orelse)),
            TryFinally: lambda: (rec(tree.body)
                                if len(tree.body) == 1 and isinstance(tree.body[0], ast.TryExcept)
                                else tabs + "try:" + irec(tree.body)) +
                                tabs + "finally:" + irec(tree.finalbody),
            ExceptHandler: lambda: tabs + "except" +
                                mix(" ", rec(tree.type)) +
                                mix(" as ", rec(tree.name)) + ":" +
                                irec(tree.body),
            ClassDef:   lambda: "\n" + "".join(tabs + "@" + rec(dec) for dec in tree.decorator_list) +
                                tabs + "class " + tree.name +
                                mix("(", jmap(", ", rec, tree.bases), ")") + ":" +
                                irec(tree.body),
            FunctionDef: lambda: "\n" + "".join(tabs + "@" + rec(dec) for dec in tree.decorator_list) +
                                tabs + "def " + tree.name + "(" + rec(tree.args) + "):" + irec(tree.body),
            For:        lambda: tabs + "for " + rec(tree.target) + " in " +
                                rec(tree.iter) + ":" + irec(tree.body) +
                                mix(tabs, "else: ", irec(tree.orelse)),
            If:         lambda: tabs + "if " + rec(tree.test) + ":" + irec(tree.body) +
                                # this doesn't collapse nested ifs into elifs
                                mix(tabs, "else:", irec(tree.orelse)),
            While:      lambda: tabs + "while " + rec(tree.test) + ":" + irec(tree.body) +
                                mix(tabs, "else:", irec(tree.orelse)),
            With:       lambda: tabs + "with " + rec(tree.context_expr) +
                                mix(" as ", tree.optional_vars) +
                                irec(tree.body),
            #Expressions
            #Str doesn't properly handle from __future__ import unicode_literals
            Str:        lambda: repr(tree.s),
            Name:       lambda: tree.id,
            Repr:       lambda: "`" + rec(tree.value) + "`",
            Num:        lambda: (lambda repr_n:
                                    "(" + repr_n.replace("inf", INFSTR) + ")"
                                    if repr_n.startswith("-")
                                    else repr_n.replace("inf", INFSTR)
                                )(repr(tree.n)),
            List:       lambda: "[" + jmap(", ", rec, tree.elts) + "]",
            ListComp:   lambda: "[" + rec(tree.elt) + jmap("", rec, tree.generators) + "]",
            GeneratorExp: lambda: "(" + rec(tree.elt) + jmap("", rec, tree.generators) + ")",
            SetComp:    lambda: "{" + rec(tree.elt) + jmap("", rec, tree.generators) + "}",
            DictComp:   lambda: "{" + rec(tree.key) + ": " + rec(tree.value) + jmap("", rec, tree.generators) + "}",
            comprehension:  lambda: " for " + rec(tree.target) + " in " + rec(tree.iter) + jmap("", lambda x: " if " + rec(x), tree.ifs),
            IfExp:      lambda: "(" + rec(tree.body) + " if " + rec(tree.test) + " else " + rec(tree.orelse) + ")",
            Set:        lambda: "{" + jmap(", ", rec, tree.elts) + "}",
            Dict:       lambda: "{" + jmap(", ", lambda x, y: rec(x) + ":" + rec(y), tree.keys, tree.values) + "}",
            Tuple:      lambda: "(" + jmap(", ", rec, tree.elts) + ("," if len(tree.elts) == 1 else "") + ")",
            UnaryOp:    lambda: "(" + unop[tree.op.__class__] +
                                ("(" + rec(tree.operand) + ")"
                                 if type(tree.op) is USub and type(tree.operand) is Num
                                 else rec(tree.operand)) + ")",
            BinOp:      lambda: "(" + rec(tree.left) + " " + binop[tree.op.__class__] + " " + rec(tree.right) + ")",
            Compare:    lambda: "(" + rec(tree.left) + jmap("", lambda op, c: " " + cmpops[op.__class__] + " " + rec(c), tree.ops, tree.comparators) + ")",
            BoolOp:     lambda: "(" + jmap(" " + boolops[tree.op.__class__] + " ", rec, tree.values) + ")",
            Attribute:  lambda: rec(tree.value) + (" " if isinstance(tree.value, Num) and isinstance(tree.value.n, int) else "") + "." + tree.attr,
            Call:       lambda: rec(tree.func) + "(" +
                        ", ".join(
                            map(rec, tree.args) +
                            map(rec, tree.keywords) +
                            box(mix("*", rec(tree.starargs))) +
                            box(mix("**", rec(tree.kwargs)))
                        ) + ")",
            Subscript:  lambda: rec(tree.value) + "[" + rec(tree.slice) + "]",
            Ellipsis:   lambda: "...",
            Index:      lambda: str(tree.value),
            Slice:      lambda: rec(tree.lower) + ":" + rec(tree.upper) + mix(":", rec(tree.step)),
            ExtSlice:   lambda: jmap(", ", rec, tree.dims),
            arguments:  lambda: ", ".join(
                            map(lambda a, d: rec(a) + mix("=", rec(d)),
                                tree.arguments,
                                [None] * (len(tree.args) - len(tree.defaults)) + tree.defaults
                            ) +
                            box(mix("*", tree.vararg)) +
                            box(mix("**", tree.kwarg))
                        ),
            keyword:    lambda: tree.arg + "=" + rec(tree.value),
            Lambda:     lambda: "(lambda " + rec(tree.args) + ": "+ rec(tree.body) + ")",
            alias:      lambda: tree.name + mix(" as ", tree.asname)
        }

        return type_dict[tree.__class__]()

    return trec(tree, 0)