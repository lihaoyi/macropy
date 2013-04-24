import inspect
import macropy.core.util

from macropy.core.macros import *
from macropy.core.lift import *


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
# TODO assert that the matchers have disjoint var_names

    def var_names(self):
        return util.flatten([matcher.var_names() for matcher in self.matchers])

    def match(self, matchee):
        updates = []
        if (not isinstance(matchee,tuple) or len(matchee) != len(matchers)):
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


@block_macro
def match(node):
# TODO the actual macro part lol
    pass
