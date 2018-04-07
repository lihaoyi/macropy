# -*- coding: utf-8 -*-
"""Macro to easily define recursive-descent PEG parsers"""

import ast
from collections import defaultdict
import re

import macropy.core.macros
import macropy.core.util
import macropy.core.walkers

from macropy.core import ast_repr, Captured   # noqa: F401
from macropy.core.hquotes import macros, hq, u, ast_literal
from macropy.quick_lambda import macros, f  # noqa: F811
from macropy.case_classes import macros, case  # noqa: F811


"""
PEG Parser Atoms
================
Sequence: e1 e2             ,       Seq
Ordered choice: e1 / e2     |       Or
Zero-or-more: e*            .rep    Rep
One-or-more: e+             .rep1
Optional: e?                .opt
And-predicate: &e           &       And
Not-predicate: !e           -       Not
"""

macros = macropy.core.macros.Macros()  # noqa: F811


@macros.block  # noqa: F811
def peg(tree, gen_sym, **kw):
    """Macro to easily define recursive-descent PEG parsers"""
    potential_targets = [
        target.id for stmt in tree
        if type(stmt) is ast.Assign
        for target in stmt.targets
    ]

    for statement in tree:
        if type(statement) is ast.Assign:
            new_tree = process(statement.value, potential_targets, gen_sym)
            statement.value = hq[
                Parser.Named(lambda: ast_literal[new_tree],
                             [u[statement.targets[0].id]])
            ]

    return tree


@macros.expr  # noqa: F811
def peg(tree, gen_sym, **kw):
    """Macro to easily define recursive-descent PEG parsers"""
    return process(tree, [], gen_sym)


def process(tree, potential_targets, gen_sym):  # noqa: F811
    @macropy.core.walkers.Walker
    def PegWalker(tree, stop, collect, **kw):
        if type(tree) is ast.Str:
            stop()
            return hq[Parser.Raw(ast_literal[tree])]
        if type(tree) is ast.Name and tree.id in potential_targets:
            collect(tree.id)
        if type(tree) is ast.BinOp and type(tree.op) is ast.RShift:
            tree.left, b_left = PegWalker.recurse_collect(tree.left)
            tree.right = hq[lambda bindings: ast_literal[tree.right]]
            names = macropy.core.util.distinct(macropy.core.util.flatten(b_left))
            tree.right.args.defaults = [hq[[]]] * len(names)
            tree.right.args.args = list(map(f[ast.arg(_, None)], names))
            tree.right.args.kwarg = ast.arg(gen_sym("kw"), None)
            stop()
            return tree

        if type(tree) is ast.BinOp and type(tree.op) is ast.FloorDiv:
            tree.left, b_left = PegWalker.recurse_collect(tree.left)
            stop()
            collect(b_left)
            return tree

        if type(tree) is ast.Tuple:
            result = hq[Parser.Seq([])]

            result.args[0].elts = tree.elts
            all_bindings = []
            for i, elt in enumerate(tree.elts):
                result.args[0].elts[i], bindings = PegWalker.recurse_collect(tree.elts[i])
                all_bindings.append(bindings)
            stop()
            collect(all_bindings)
            return result

        if type(tree) is ast.Compare and type(tree.ops[0]) is ast.Is:
            left_tree, bindings = PegWalker.recurse_collect(tree.left)
            new_tree = hq[ast_literal[left_tree].bind_to(u[tree.comparators[0].id])]
            stop()
            collect(bindings + [tree.comparators[0].id])
            return new_tree

    new_tree = PegWalker.recurse(tree)
    return new_tree


def cut():
    """Used within a Seq parser (p1, p2, p3,...) to commit the Seq to that
    alternative.

    After the Seq passes the `cut`, any failure becomes fatal, and backtracking
    is not performed. This improves performance and improves the quality
    of the error messages."""


@case
class Input(string, index):  # noqa: F821
    pass


@case
class Success(output, bindings, remaining):  # noqa: F821
    """
    output: the final value that was parsed
    bindings: named value bindings, created by the `is` keyword
    remaining: an Input representing the unread portion of the input
    """
    pass


@case
class Failure(remaining, failed, fatal | False):  # noqa: F821
    """
    remaining: an Input representing the unread portion of the input
    failed: a List[Parser], containing the stack of parsers in
            effect at time of failure
    fatal: whether a parent parser which receives this result from a child
           should continue backtracking
    """
    @property
    def index(self):
        return self.remaining.index

    @property
    def trace(self):
        return [x for f in self.failed for x in f.trace_name]

    @property
    def msg(self):
        """A pretty human-readable error message representing this Failure"""
        line_length = 60

        string = self.remaining.string
        index = self.index
        line_start = string.rfind('\n', 0, index+1)

        line_end = string.find('\n', index+1, len(string))
        if line_end == -1:
            line_end = len(string)

        line_num = string.count('\n', 0, index)

        offset = min(index - line_start, 40)

        msg = ("index: " + str(self.index) + ", line: " + str(line_num + 1) +
               ", col: " + str(index - line_start) + "\n" +
               " / ".join(self.trace) + "\n" +
               string[line_start+1:line_end] [index - offset - line_start:index+line_length-offset - line_start] + "\n" +
               (offset-1) * " " + "^" + "\n" +
               "expected: " + self.failed[-1].short_str())
        return msg


class ParseError(Exception):
    """An exception that wraps a Failure"""
    def __init__(self, failure):
        self.failure = failure
        Exception.__init__(self, failure.msg)


@case
class Parser:
    def parse(self, string):
        """String -> value; throws ParseError in case of failure"""
        res = Parser.Full(self).parse_input(Input(string, 0))
        if type(res) is Success:
            return res.output
        else:
            raise ParseError(res)

    def parse_partial(self, string):
        """String -> Success | Failure"""
        return self.parse_input(Input(string, 0))

    def parse_string(self, string):
        """String -> Success | Failure"""
        return Parser.Full(self).parse_input(Input(string, 0))

    def parse_input(self, input):
        """Input -> Success | Failure"""

    @property
    def trace_name(self):
        return []

    def bind_to(self, string):
        return Parser.Named(lambda: self, [string])

    def __and__(self, other): return Parser.And([self, other])

    def __or__(self, other): return Parser.Or([self, other])

    def __neg__(self): return Parser.Not(self)

    @property
    def join(self):
        return self // "".join
    @property
    def rep1(self):
        return Parser.And([Parser.Rep(self), self])

    @property
    def rep(self):
        return Parser.Rep(self)

    def rep1_with(self, other):
        return (Parser.Seq([self, Parser.Seq([other, self]).rep]) //
                (lambda x: [x[0]] + [y[1] for y in x[1]]))

    def rep_with(self, other):
        return self.rep1_with(other) | Parser.Succeed([])

    @property
    def opt(self):
        return Parser.Or([self, Parser.Raw("")])

    @property
    def r(self):
        """Creates a regex-matching parser from the given raw parser"""
        return Parser.Regex(self.string)

    def __mul__(self, n): return Parser.RepN(self, n)

    def __floordiv__(self, other): return Parser.Transform(self, other)

    def __pow__(self, other): return Parser.Transform(self, lambda x: other(*x))

    def __rshift__(self, other): return Parser.TransformBound(self, other)

    class Full(parser):  # noqa: F821
        def parse_input(self, input):
            res = self.parser.parse_input(input)
            if type(res) is Success and res.remaining.index < len(input.string):
                return Failure(res.remaining, [self])
            else:
                return res
        def short_str(self):
            return self.parser.short_str()

    class Raw(string):
        def parse_input(self, input):
            if input.string[input.index:].startswith(self.string):
                return Success(self.string, {}, input.copy(index = input.index + len(self.string)))
            else:
                return Failure(input, [self])

        def short_str(self):
            return repr(self.string)

    class Regex(regex_string):
        def parse_input(self, input):
            match = re.match(self.regex_string, input.string[input.index:])
            if match:
                group = match.group()
                return Success(group, {},
                               input.copy(index=input.index + len(group)))
            else:
                return Failure(input, [self])

        def short_str(self):
            return repr(self.regex_string) + ".r"

    class Seq(children):  # noqa: F821
        def parse_input(self, input):
            current_input = input
            results = []
            result_dict = defaultdict(lambda: [])
            committed = False
            for child in self.children:
                if child is cut:
                    committed = True
                else:
                    res = child.parse_input(current_input)

                    if type(res) is Failure:
                        if committed or res.fatal:
                            return Failure(res.remaining, [self] + res.failed, True)
                        else:
                            return res

                    current_input = res.remaining
                    results.append(res.output)
                    for k, v in res.bindings.items():
                        result_dict[k] = v

            return Success(results, result_dict, current_input)

        def short_str(self):
            return "(" + ", ".join(map(lambda x: x.short_str(), self.children)) + ")"

    class Or(children):  # noqa: F821
        def parse_input(self, input):
            for child in self.children:
                res = child.parse_input(input)

                if type(res) is Success:
                    return res
                elif res.fatal:
                    res.failed = [self] + res.failed
                    return res
            return Failure(input, [self])

        def __or__(self, other): return Parser.Or(self.children + [other])

        def short_str(self):
            return "(" + " | ".join(map(lambda x: x.short_str(), self.children)) + ")"

    class And(children):  # noqa: F821
        def parse_input(self, input):
            results = [child.parse_input(input) for child in self.children]
            failures = [res for res in results if type(res) is Failure]
            if failures == []:
                return results[0]
            else:
                failures[0].failed = [self] + failures[0].failed
                return failures[0]

        def __and__(self, other): return Parser.And(self.children + [other])

        def short_str(self):
            return "(" + " & ".join(map(lambda x: x.short_str(), self.children)) + ")"

    class Not(parser):  # noqa: F821
        def parse_input(self, input):
            if type(self.parser.parse_input(input)) is Success:
                return Failure(input, [self])
            else:
                return Success(None, {}, input)

        def short_str(self):
            return "-" + self.parser.short_str()

    class Rep(parser):  # noqa: F821
        def parse_input(self, input):
            current_input = input
            results = []
            result_dict = defaultdict(lambda: [])

            while True:
                res = self.parser.parse_input(current_input)
                if type(res) is Failure:
                    if res.fatal:
                        res.failed = [self] + res.failed
                        return res
                    else:
                        return Success(results, result_dict, current_input)

                current_input = res.remaining

                for k, v in res.bindings.items():
                    result_dict[k] = result_dict[k] + [v]

                results.append(res.output)

    class RepN(parser, n):  # noqa: F821
        def parse_input(self, input):
            current_input = input
            results = []
            result_dict = defaultdict(lambda: [])

            for i in range(self.n):
                res = self.parser.parse_input(current_input)
                if type(res) is Failure:
                    res.failed = [self] + res.failed
                    return res

                current_input = res.remaining

                for k, v in res.bindings.items():
                    result_dict[k] = result_dict[k] + [v]

                results.append(res.output)

            return Success(results, result_dict, current_input)

        def short_str(self):
            return self.parser.short_str() + "*" + n

    class Transform(parser, func):  # noqa: F821
        def parse_input(self, input):
            res = self.parser.parse_input(input)

            if type(res) is Success:
                res.output = self.func(res.output)
            else:
                res.failed = [self] + res.failed
            return res

        def short_str(self):
            return self.parser.short_str()

    class TransformBound(parser, func):  # noqa: F821
        def parse_input(self, input):
            res = self.parser.parse_input(input)
            if type(res) is Success:
                res.output = self.func(**res.bindings)
                res.bindings = {}
            else:
                res.failed = [self] + res.failed
            return res

        def short_str(self):
            return self.parser.short_str()

    class Named(parser_thunk, trace_name):  # noqa: F821
        self.stored_parser = None  # noqa: F821

        @property
        def parser(self):
            if not self.stored_parser:
                self.stored_parser = self.parser_thunk()
            return self.stored_parser

        def parse_input(self, input):
            res = self.parser.parse_input(input)
            if type(res) is Success:
                res.bindings = {self.trace_name[0]: res.output}
            else:
                res.failed = [self] + res.failed
            return res

        def short_str(self):
            return self.trace_name[0]

    class Succeed(string):  # noqa: F821
        def parse_input(self, input):
            return Success(self.string, {}, input)

    class Fail():
        def parse_input(self, input):
            return Failure(input, [self])

        def short_str(self):
            return "fail"
