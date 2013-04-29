import inspect

from ast import *
from macropy.core import util
from macropy.core.macros import *
from macropy.core.lift import macros
from macropy.core.lift import *


class PatternMatchException(Exception):
    pass


class PatternVarConflict(Exception):
    pass


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
        returns False.  """
        pass

    def match_value(self, matchee, should_raise):
        results = self.match(matchee)
        self.var_dict = {}
        if not results:
            if should_raise:
                raise PatternMatchException()
            return False
        for (varname, value) in results[1]:
            self.var_dict[varname] = value

    def get_var(self, var_name):
        return self.var_dict[var_name]
        

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
        if not _vars_are_disjoint(util.flatten([m.var_names() for m in
            matchers])):
            raise PatternVarConflict()

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
    def __init__(self, *matchers):
        self.matchers = matchers
        if not _vars_are_disjoint(util.flatten([m.var_names() for m in
            matchers])):
            raise PatternVarConflict()

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
        if not _vars_are_disjoint(util.flatten([m.var_names() for m in
            argMatchers])):
            raise PatternVarConflict()

    def var_names(self):
        return util.flatten([matcher.var_names() for matcher in self.argMatchers])

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


def build_matcher(node, modified):
    if isinstance(node, Num):
        return q%(LiteralMatcher(u%(node.n)))
    if isinstance(node, Str):
        return q%(LiteralMatcher(u%(node.s)))
    if isinstance(node, Name):
        if node.id in ['True', 'False']:
            return q%(LiteralMatcher(ast%(node)))
        modified.add(node.id)
        return q%(NameMatcher(u%(node.id)))
    if isinstance(node, List):
        sub_matchers = []
        for child in node.elts:
            sub_matchers.append(build_matcher(child, modified))
        return Call(Name('ListMatcher', Load()), sub_matchers, [], None, None)
    if isinstance(node, Tuple):
        sub_matchers = []
        for child in node.elts:
            sub_matchers.append(build_matcher(child, modified))
        return Call(Name('TupleMatcher', Load()), sub_matchers, [], None, None)
    if isinstance(node, Call):
        sub_matchers = []
        for child in node.args:
            sub_matchers.append(build_matcher(child, modified))
        return Call(Name('ClassMatcher', Load()), [node.func] + sub_matchers,
                [], None, None)
    raise Exception("Unrecognized node " + repr(node))


def _is_pattern_match_stmt(node):
    return (isinstance(node, Expr) and 
            _is_pattern_match_expr(node.value))
            

def _is_pattern_match_expr(node):
    return (isinstance(node, BinOp) and
            isinstance(node.op, LShift))


@block_macro
def matching(node):
    """
    This macro will enable non-refutable pattern matching.  If a pattern match
    fails, an exception will be thrown.
    """
    @Walker
    def func(node):
        if _is_pattern_match_stmt(node):
            modified = set()
            matcher = build_matcher(node.value.left, modified) 
            # lol random names for hax
            with q as assignment:
                xsfvdy = ast%(matcher)
            statements = [assignment,
                          Expr(q%(xsfvdy.match_value(ast%(node.value.right),
                              True)))]
            for var_name in modified:
                statements.append(Assign([Name(var_name, Store())],
                    q%(xsfvdy.get_var(u%var_name))))
            return statements
        else:
            return node
    func.recurse(node)
    return node.body


def _rewrite_if(node):
    # with q as rewritten:
    #     try:
    #         with matching:
    #             u%(matchPattern)
    #         u%(successBody)
    #     except PatternMatchException:
    #         u%(_maybe_rewrite_if(failBody))
    # return rewritten
    handler = ExceptHandler(Name('PatternMatchException',
        Load()), None, node.orelse)
    try_stmt = TryExcept(node.body, [handler], [])
    macroed_match = With(Name('matching', Load()), None, Expr(node.test))
    try_stmt.body = [macroed_match] + try_stmt.body
    if len(handler.body) == 1:
        handler.body = [_maybe_rewrite_if(handler.body[0])]
    elif not handler.body:
        handler.body = [Pass()]
    return try_stmt


def _maybe_rewrite_if(stmt):
    if isinstance(stmt, If) and _is_pattern_match_expr(stmt.test):
        return _rewrite_if(stmt)
    return stmt

@block_macro
def case_switch(node):
    """
    This only enables (refutable) pattern matching in top-level if statements.
    The advantage of this is the limited reach ensures less interference with
    existing code.
    """
    for i in xrange(len(node.body)):
        node.body[i] = _maybe_rewrite_if(node.body[i])
    print unparse(node.body)
    return node.body
