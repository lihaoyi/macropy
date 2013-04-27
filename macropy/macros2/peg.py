import re

from macropy.core.macros import *
from macropy.core.lift import macros, q, u
from macropy.macros.adt import case, NO_ARG
import re
macros = True


@expr_macro
def peg(tree):
    return parser(tree)

def parser(tree):

    if type(tree) is Str:
        return q%Raw(u%tree)

    if type(tree) is UnaryOp:
        if type(tree.op) is UAdd:   return q%rep1(u%parser(tree.operand))
        if type(tree.op) is USub:   return q%Not(u%parser(tree.operand))
        if type(tree.op) is Invert: return q%Rep(u%parser(tree.operand))

    if type(tree) is BinOp:
        if type(tree.op) is BitOr:
            left = parser(tree.left)
            right = parser(tree.right)
            result = q%Or([])
            result.args[0].elts = [left, right]
            return result

        if type(tree.op) is BitAnd:
            left = parser(tree.left)
            right = parser(tree.right)
            result = q%And([])
            result.args[0].elts = [left, right]
            return result

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
        return self.parse_input(Input(string, 0))


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