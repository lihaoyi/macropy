import re

from macropy.core.macros import *
from macropy.core.lift import macros, q, u
from macropy.macros.quicklambda import macros, f
from macropy.macros.adt import macros, case, NO_ARG
import re
from collections import defaultdict
macros = Macros()

@macros.block
def peg(tree):
    for statement in tree.body:
        if type(statement) is Assign:
            new_tree, bindings = _recurse(statement.value, [])
            statement.value = q%(Lazy(lambda: ast%new_tree))


    return tree.body


@macros.expr
def peg(tree):
    new_tree, bindings = _recurse(tree, [])
    return new_tree


def _recurse(tree, bindings):
    if type(tree) is Str:
        return q%Raw(ast%tree), bindings

    if type(tree) is UnaryOp:
        (tree.operand, bindings) = _recurse(tree.operand, bindings)
        return tree, bindings

    if type(tree) is BinOp and type(tree.op) is RShift:
        tree.left, b_left = _recurse(tree.left, [])
        tree.right = q%(lambda bindings: ast%tree.right)

        tree.right.args.args = map(f%Name(id = _), b_left)
        return tree, b_left

    if type(tree) is BinOp and type(tree.op) is FloorDiv:
        tree.left, b_left = _recurse(tree.left, bindings)
        return tree, b_left

    if type(tree) is BinOp:
        tree.left, b_left = _recurse(tree.left, bindings)
        tree.right, b_right = _recurse(tree.right, b_left)
        return tree, b_right

    if type(tree) is Tuple:
        result = q%Seq([])

        result.args[0].elts = tree.elts
        for i, elt in enumerate(tree.elts):
            result.args[0].elts[i], bindings = _recurse(tree.elts[i], bindings)

        return result, bindings

    if type(tree) is Call:
        for i, elt in enumerate(tree.args):
            tree.args[i], bindings = _recurse(tree.args[i], bindings)
        tree.func, bindings = _recurse(tree.func, bindings)
        return tree, bindings

    if type(tree) is Attribute:
        tree.value, bindings = _recurse(tree.value, bindings)
        return tree, bindings

    if type(tree) is Compare and type(tree.ops[0]) is Is:
        left_tree, bindings = _recurse(tree.left, bindings)
        new_tree = q%(ast%left_tree).bind_to(u%len(bindings))
        return new_tree, bindings + [tree.comparators[0].id]

    return tree, bindings

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

    def bind_to(self, string):
        return Binder(self, string)

    def parse(self, string):
        res = self.parse_input(Input(string, 0))
        if res is None:
            return None

        out, bindings, remaining_input = res
        return [out]

    def parse_all(self, string):
        res = self.parse_input(Input(string, 0))
        if res is None:
            return None

        (out, bindings, remaining_input) = res
        if remaining_input.index != len(string):
            return None

        return [out]


    def __and__(self, other):   return And([self, other])

    def __or__(self, other):    return Or([self, other])

    def __neg__(self):          return Not(self)

    @property
    def rep1(self):
        return And([Rep(self), self])

    @property
    def rep(self):
        return Rep(self)

    @property
    def opt(self):
        return Or([self, Raw("")])

    @property
    def r(self):
        """Creates a regex-matching parser from the given raw parser"""
        return Regex(self.string)
    def __mul__(self, n):   return RepN(self, n)

    def __floordiv__(self, other):   return Transform(self, other)

    def __pow__(self, other):   return Transform(self, lambda x: other(*x))

    def __rshift__(self, other): return TransformBound(self, other)


    class Raw(string):
        def parse_input(self, input):
            if input.string[input.index:].startswith(self.string):
                return self.string, {}, input.copy(index = input.index + len(self.string))
            else:
                return None

    class Regex(regex_string):
        def parse_input(self, input):
            match = re.match(self.regex_string, input.string[input.index:])
            if match:
                group = match.group()
                return group, {}, input.copy(index = input.index + len(group))
            else:
                return None

    class NChildParser:
        class Seq(children):
            def parse_input(self, input):
                current_input = input
                results = []
                result_dict = defaultdict(lambda: [])
                for child in self.children:
                    res = child.parse_input(current_input)
                    if res is None: return None

                    (res, bindings, current_input) = res
                    results.append(res)
                    for k, v in bindings.items():
                        result_dict[k] = v

                return (results, result_dict, current_input)


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
                    return (None, {}, input)


        class Rep(parser):
            def parse_input(self, input):
                current_input = input
                results = []
                result_dict = defaultdict(lambda: [])

                while True:
                    res = self.parser.parse_input(current_input)
                    if res is None: return (results, result_dict, current_input)

                    (res, bindings, current_input) = res

                    for k, v in bindings.items():
                        result_dict[k] = result_dict[k] + [v]

                    results.append(res)

        class RepN(parser, n):
            def parse_input(self, input):
                current_input = input
                results = []
                result_dict = defaultdict(lambda: [])

                for i in range(self.n):
                    res = self.parser.parse_input(current_input)
                    if res is None: return None

                    (res, bindings, current_input) = res

                    for k, v in bindings.items():
                        result_dict[k] = result_dict[k] + [v]

                    results.append(res)

                return (results, result_dict, current_input)
        class Transform(parser, func):

            def parse_input(self, input):
                result = self.parser.parse_input(input)
                if result is None:
                    return None
                else:
                    res, bindings, new_input = result
                    return self.func(res), bindings, new_input

        class TransformBound(parser, func):

            def parse_input(self, input):
                result = self.parser.parse_input(input)
                if result is None:
                    return None
                else:
                    res, bindings, new_input = result
                    binding_list = map(f%_[1], sorted(bindings.items()))
                    return self.func(*binding_list), {}, new_input

        class Binder(parser, name):
            def parse_input(self, input):
                result = self.parser.parse_input(input)
                if result is None: return None
                result, bindings, new_input = result

                bindings[self.name] = result
                return result, bindings, new_input

        class Lazy(parser_thunk):
            def parse_input(self, input):
                if not isinstance(self.parser_thunk, Parser):
                    self.parser_thunk = self.parser_thunk()
                return self.parser_thunk.parse_input(input)


    class Success(string):
        def parse_input(self, input):
            return (self.string, {}, input)


    class Failure():
        def parse_input(self, input):
            return None







