import inspect

from ast import *
from macropy.core import util
from macropy.core.macros import *
from macropy.core.lift import *


def _vars_are_disjoint(var_names):
    return len(var_names) == len(set(var_names))

class Matcher(object):
    def __init__(self):
        pass

    def var_names(self):
        """
        Returns a container of the variable names which may be modified upon a
        successful match.
        """
        pass
    
    def match(self, matchee):
        """
        Returns (True, [(varname, value)...]) if there is a match.  Otherwise,
        returns False.
        """
        pass

    def match_update_locals(self, matchee, locals_dict):
        result = self.match(matchee)
        if result:
            for (varname, value) in result[1]:
                locals_dict[varname] = value
            return True
        return False


class LiteralMatcher(Matcher):
    def __init__(self, val):
        self.val = val

    def var_names(self):
        return []

    def match(self, matchee):
        if self.val == matchee:
            return (True, [])
        return False
    

class TupleMatcher(Matcher):
    def __init__(self, *matchers):
        self.matchers = matchers
        assert _vars_are_disjoint(util.flatten([m.var_names() for m in
            matchers]))

    def var_names(self):
        return util.flatten([matcher.var_names() for matcher in self.matchers])

    def match(self, matchee):
        updates = []
        if (not isinstance(matchee,tuple) or len(matchee) != len(self.matchers)):
            return False
        for (matcher, sub_matchee) in zip(self.matchers, matchee):
            match = matcher.match(sub_matchee)
            if not match:
                return False
            updates.extend(match[1])
        return (True, updates)


class ListMatcher(Matcher):
    def __init__(self, matchers):
        self.matchers = matchers
        assert _vars_are_disjoint(util.flatten([m.var_names() for m in
            matchers]))

    def var_names(self):
        return util.flatten([matcher.var_names() for matcher in self.matchers])

    def match(self, matchee):
        updates = []
        if (not isinstance(matchee,list) or len(matchee) != len(matchers)):
            return False
        for (matcher, sub_matchee) in zip(self.matchers, matchee):
            match = matcher.match(sub_matchee)
            if not match:
                return False
            updates.extend(match[1])
        return (True, updates)


class NameMatcher(Matcher):
    def __init__(self, name):
        self.name = name

    def var_names(self):
        return [self.name]

    def match(self, matchee):
        return (True, [(self.name, matchee)])


# Currently only works for positional arguments
class ClassMatcher(Matcher):
    def __init__(self, clazz, *argMatchers):
        self.clazz = clazz
        self.argMatchers = argMatchers
        arg_field_names = []
        arg_spec = inspect.getargspec(clazz.__init__)
        for arg in arg_spec.args:
            if arg is not 'self':
                arg_field_names.append(arg)
        self.arg_field_names = arg_field_names

    def var_names(self):
        return util.flatten([matcher.var_names() for matcher in self.matchers])

    def match(self, matchee):
        updates = []
        if isinstance(matchee, self.clazz):
            sub_matchees = []
            for field_name in self.arg_field_names:
                sub_matchees.append(getattr(matchee, field_name))
            for (matcher, sub_matchee) in zip(self.argMatchers, sub_matchees):
                match = matcher.match(sub_matchee)
                if not match:
                    return False
                updates.extend(match[1])
            return (True, updates)
        return False

def build_matcher(node):
    if isinstance(node, Num):
        return q%(LiteralMatcher(u%(node.n)))
    if isinstance(node, String):
        return q%(LiteralMatcher(u%(node.s)))
    if isinstance(node, Name):
        return q%(NameMatcher(u%(node.id)))
    if isinstance(node, List):
        sub_matchers = []
        for child in node.elts:
            sub_matchers.append(build_matcher(child))
        return Call(Name('ListMatcher'), *sub_matchers)
    if isinstance(node, Tuple):
        sub_matchers = []
        for child in node.elts:
            sub_matchers.append(build_matcher(child))
        return Call(Name('TupleMatcher'), *sub_matchers)
    if isinstance(node, Call):
        sub_matchers = []
        for child in node.args:
            sub_matchers.append(build_matcher(child))
        return Call(Name('ClassMatcher'), node.func, *sub_matchers)
    raise Exception("Unrecognized node " + repr(node))


@block_macro
def matching(node):
    @Walker
    def func(node):
        if isinstance(node, BinOp) and node.op == LShift:
            return q%((u%(build_matcher(node.left))).match_update_locals(
                u%(node.right), locals()))
        else:
            return node
    func.recurse(node)
    return node
