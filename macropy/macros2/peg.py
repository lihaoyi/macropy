import re

from macropy.core.macros import *
from macropy.core.lift import macros, q, u
from macropy.macros.adt import case, NO_ARG
import re
macros = True

@block_macro
def peg(tree):
    for statement in tree.body:
        if type(statement) is Assign:
            statement.value = q%(Lazy(lambda: u%parser(statement.value)))

    return tree.body


@expr_macro
def peg(tree):
    return parser(tree)

def parser(tree):

    if type(tree) is Str:
        return q%Raw(u%tree)

    if type(tree) is UnaryOp:
        tree.operand = parser(tree.operand)
        return tree

    if type(tree) is BinOp:
        tree.left = parser(tree.left)
        tree.right = parser(tree.right)
        return tree

    if type(tree) is Tuple:
        result = q%Seq([])
        result.args[0].elts = map(parser, tree.elts)
        return result

    if type(tree) is Call:
        tree.args = map(parser, tree.args)
        tree.func = parser(tree.func)
        return tree

    return tree

"""
PEG Parser Atoms
================
Sequence: e1 e2             ,   8       Seq
Ordered choice: e1 / e2     |   7       Or
Zero-or-more: e*            ~   13      Rep
One-or-more: e+             +   13      rep1
Optional: e?                            opt
And-predicate: &e           &   9       And
Not-predicate: !e           -   13      Not

"""

@case
class Input(string, index):
    pass

@case
class Parser:
    def parse(self, string):
        res = self.parse_input(Input(string, 0))
        if res is None:
            return None

        out, remaining_input = res
        return [out]

    def parse_all(self, string):
        res = self.parse_input(Input(string, 0))
        if res is None:
            return None

        (out, remaining_input) = res
        if remaining_input.index != len(string):
            return None

        return [out]


    def __and__(self, other):   return And([self, other])

    def __or__(self, other):    return Or([self, other])

    def __neg__(self):          return Not(self)

    def __pos__(self):          return rep1(self)

    def __invert__(self):       return Rep(self)

    def __mul__(self, other):   return Transform(self, other)

    def __pow__(self, other):   return Transform(self, lambda x: other(*x))

    class Raw(string):
        def parse_input(self, input):
            if input.string[input.index:].startswith(self.string):
                return self.string, input.copy(index = input.index + len(self.string))
            else:
                return None

    class Regex(regex_string):
        def parse_input(self, input):
            match = re.match(self.regex_string, input.string[input.index:])
            if match:
                group = match.group()
                return group, input.copy(index = input.index + len(group))
            else:
                return None
    class NChildParser:

        class Seq(children):
            def parse_input(self, input):
                current_input = input
                results = []
                for child in self.children:
                    res = child.parse_input(current_input)
                    if res is None: return None

                    (res, current_input) = res
                    results.append(res)
                return (results, current_input)


        class Or(children):
            def parse_input(self, input):
                for child in self.children:
                    res = child.parse_input(input)
                    if res != None: return res

                return None

        class And(children):
            def parse_input(self, input):
                results = [child.parse_input(input) for child in self.children]
                if all(results):
                    return results[0]

                return None

    class OneChildParser:
        class Not(parser):
            def parse_input(self, input):
                if self.parser.parse_input(input):
                    return None
                else:
                    return (None, input)


        class Rep(parser):
            def parse_input(self, input):
                current_input = input
                results = []

                while True:
                    res = self.parser.parse_input(current_input)
                    if res is None: return (results, current_input)

                    (res, current_input) = res
                    results.append(res)

        class Transform(parser, func):

            def parse_input(self, input):
                result = self.parser.parse_input(input)
                if result is None:
                    return None
                else:
                    res, new_input = result
                    return self.func(res), new_input

        class Lazy(parser_thunk):
            def parse_input(self, input):
                if not isinstance(self.parser_thunk, Parser):
                    self.parser_thunk = self.parser_thunk()
                return self.parser_thunk.parse_input(input)


    class Success(string):
        def parse_input(self, input):
            return (self.string, input)


    class Failure():
        def parse_input(self, input):
            return None




def rep1(parser):
    return And([Rep(parser), parser])

def opt(parser):
    return Or([parser, Raw("")])

def r(parser):
    return Regex(parser.string)