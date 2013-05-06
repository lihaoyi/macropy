import inspect

from ast import *
from macropy.core import util
from macropy.core.macros import *
from macropy.core.lift import macros
from macropy.core.lift import *

macros = Macros()

class PatternMatchException(Exception):
    """
    Thrown when a nonrefutable pattern match fails
    """
    pass


class PatternVarConflict(Exception):
    """
    Thrown when a pattern attempts to match a variable more than once.
    """
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
        Returns ([(varname, value)...]) if there is a match.  Otherwise,
        raise PatternMatchException().  This guy is recursively implemented by
        matchers, and is stateless.
        """
        pass

    def match_value(self, matchee):
        """
        Match against matchee and produce an internal dictionary of the values
        for each variable.
        """
        self.var_dict = {}
        for (varname, value) in self.match(matchee):
            self.var_dict[varname] = value

    def get_var(self, var_name):
        return self.var_dict[var_name]
        

class LiteralMatcher(Matcher):
    def __init__(self, val):
        self.val = val

    def var_names(self):
        return []

    def match(self, matchee):
        if self.val != matchee:
            raise PatternMatchException("Literal match failed")
        return []
    

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
        if (not isinstance(matchee, tuple) or 
                len(matchee) != len(self.matchers)):
            raise PatternMatchException("Expected tuple of %d elements" %
                    (len(self.matchers),))
        for (matcher, sub_matchee) in zip(self.matchers, matchee):
            match = matcher.match(sub_matchee)
            updates.extend(match)
        return updates


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
        if (not isinstance(matchee, list) or len(matchee) != len(self.matchers)):
            raise PatternMatchException("Expected list of length %d" %
                    (len(self.matchers),))
        for (matcher, sub_matchee) in zip(self.matchers, matchee):
            match = matcher.match(sub_matchee)
            updates.extend(match)
        return updates


class NameMatcher(Matcher):
    def __init__(self, name):
        self.name = name

    def var_names(self):
        return [self.name]

    def match(self, matchee):
        return [(self.name, matchee)]


# Currently only works for positional arguments
class ClassMatcher(Matcher):
    def __init__(self, clazz, positionalMatchers, **kwMatchers):
        self.clazz = clazz
        self.positionalMatchers = positionalMatchers
        self.kwMatchers = kwMatchers

        # This stores which fields of the object we will need to look at.
        if not _vars_are_disjoint(util.flatten([m.var_names() for m in
            positionalMatchers])):
            raise PatternVarConflict()


    def var_names(self):
        return (util.flatten([matcher.var_names() 
            for matcher in self.positionalMatchers]) + 
            util.flatten([matcher.var_names() for matcher in
                self.kwMatchers.values()]))


    def default_unapply(self, matchee, kw_keys):
# TODO should it fail if constructor-inspection doesn't work?
        if not isinstance(matchee, self.clazz):
            raise PatternMatchException("Matchee should be of type %r" %
                    (self.clazz,))
        pos_values = []
        kw_dict = {}
        arg_spec = inspect.getargspec(self.clazz.__init__)
        for arg in arg_spec.args:
            if arg is not 'self':
                pos_values.append(getattr(matchee, arg, None))
        # if arg_spec.varargs:
        #     pos_values.extend(getattr(matchee, varargs, []))
        for kw_key in kw_keys:
            if not hasattr(matchee, kw_key):
                raise PatternMatchException("Keyword argument match failed: no"
                        + " attribute %r" % (kw_key,))
            kw_dict[kw_key] = getattr(matchee, kw_key)
        return pos_values, kw_dict


    def match(self, matchee):
        updates = []
        if hasattr(self.clazz, '__unapply__'):
            pos_vals, kw_dict = self.clazz.__unapply__(matchee,
                    self.kwMatchers.keys())
        else:
            pos_vals, kw_dict = self.default_unapply(matchee,
                    self.kwMatchers.keys())

        for (matcher, sub_matchee) in zip(self.positionalMatchers,
                pos_vals):
            updates.extend(matcher.match(sub_matchee))
        for key, val in kw_dict.items():
            updates.extend(self.kwMatchers[key].match(val))
        return updates


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
        positional_matchers = List(sub_matchers, Load())
        kw_matchers = []
        for kw in node.keywords:
            kw_matchers.append(
                    keyword(kw.arg, build_matcher(kw.value, modified)))
        return Call(Name('ClassMatcher', Load()), [node.func,
            positional_matchers], kw_matchers, None, None)
    if (isinstance(node, BinOp) and isinstance(node.op, BitAnd)):
        # TODO parallel matching
        pass
    raise Exception("Unrecognized node " + repr(node))


def _is_pattern_match_stmt(node):
    return (isinstance(node, Expr) and 
            _is_pattern_match_expr(node.value))
            

def _is_pattern_match_expr(node):
    return (isinstance(node, BinOp) and
            isinstance(node.op, LShift))


@macros.block
def _matching(node):
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
                          Expr(q%(xsfvdy.match_value(ast%(node.value.right))))]
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
    macroed_match = With(Name('_matching', Load()), None, Expr(node.test))
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

@macros.block
def case_switch(node):
    """
    This only enables (refutable) pattern matching in top-level if statements.
    The advantage of this is the limited reach ensures less interference with
    existing code.
    """
    for i in xrange(len(node.body)):
        node.body[i] = _maybe_rewrite_if(node.body[i])
    return node.body

@macros.block
def patterns(node):
    """
    This enables patterns everywhere!  NB if you use this macro, you will not be
    able to use real left shifts anywhere.
    """
    # First transform all if-matches, then wrap the whole thing in a "with
    # _matching" block
    @Walker
    def if_rewriter(node):
        return _maybe_rewrite_if(node)
    if_rewriter.recurse(node)
    node.context_expr = Name('_matching', Load())
    return node
