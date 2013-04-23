import unittest

from macropy.core.macros import *
from macropy.core.lift import *
from macropy.macros.string_interp import *
import time


def run():
    #import sqlite3
    #conn = sqlite3.connect(":memory:")
    #cursor = conn.cursor()

    def type_dict(d):
        return lambda x: d[type(x)]

    def handleExpr(tree):

        if type(tree) is BoolOp:
            boolop_map = {
                And: "AND",
                Or: "OR"
            }

            return (" " + boolop_map(tree.op) + " ").join(handleExpr(value) for value in tree.values)
        if type(tree) is BinOp:
            binop_map = type_dict({
                Add: "+",
                Sub: "-",
                Mult: "*",
                Div: "/",
                Mod: "%",
                Pow: "**",
                LShift: "<<",
                RShift: ">>",
                BitOr: "|",
                BitXor: "",
                BitAnd: "&",
                FloorDiv: "/"
            })
            return handleExpr(tree.left) + " " + binop_map(tree.op) + " " + handleExpr(tree.right)

        if type(tree) is UnaryOp:
            unaryop_map = type_dict({
                Invert: "~",
                Not: "NOT ",
                UAdd: "+",
                USub: "-"
            })
            return unaryop_map(tree.op) + handleExpr(tree.operand)

        if type(tree) is IfExp:
            return "CASE WHEN " + handleExpr(tree.test) + " THEN " + handleExpr(tree.body) + " ELSE " + handleExpr(tree.orelse) + " END"
        if type(tree) is Compare:

            cmpop_map = type_dict({
                Eq: "=",
                NotEq: "!=",
                Lt: "<",
                LtE: "<=",
                Gt: ">",
                GtE: ">=",
                Is: "=",
                IsNot: "!=",
                In: "IN",
                NotIn: "NOT IN"
            })


            return handleExpr(tree.left) + " " + cmpop_map(tree.ops[0]) + " " + handleExpr(tree.comparators[0])

        if type(tree) is Num:
            return repr(tree.n)

        if type(tree) is Str:
            return repr(tree.s)

        if type(tree) is Attribute:
            return tree.value.id + "." + tree.attr

        if type(tree) is Name:
            return tree.id

        if type(tree) is List: pass
        if type(tree) is Tuple:
            return ", ".join([handleExpr(e) for e in tree.elts])

    def transGen(tree):
        assert type(tree) is GeneratorExp
        elt = tree.elt

        if type(elt) is Attribute:
            sel = handleExpr(elt)

        if type(elt) is Tuple:
            sel = handleExpr(elt)

        frm = " JOIN ".join(
            gen.iter.id + " " + gen.target.id
            for gen in tree.generators
        )

        all_guards = "AND".join(
            handleExpr(ifexp)
            for gen in tree.generators
            for ifexp in gen.ifs
        )

        whr = "" if all_guards == "" else "WHERE " + all_guards

        return "SELECT %s FROM %s %s" % (sel, frm, whr)
    dbA = []
    dbB = []
    treeA = q%((x.foo, y.bar) for x in dbA if x.foo > 10 for y in dbA)
    treeB = q%(x.foo for x in dbA for y in dbA)

    print transGen(treeA)
    print transGen(treeB)