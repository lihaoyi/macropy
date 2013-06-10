import inspect

from abc import ABCMeta, abstractmethod
from ast import *

from macropy.core import util
from macropy.core.macros import *

from macropy.core.quotes import macros, q
from macropy.core.hquotes import macros, hq
macros = Macros()


class PatternMatchException(Exception):
    """Thrown when a nonrefutable pattern match fails"""
    pass


class PatternVarConflict(Exception):
    """Thrown when a pattern attempts to match a variable more than once."""
    pass


def _vars_are_disjoint(var_names):
    return len(var_names)== len(set(var_names))


class Matcher(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def var_names(self):
        """
        Returns a container of the variable names which may be modified upon a
        successful match.
        """
        pass

    @abstractmethod
    def match(self, matchee):
        """
        Returns ([(varname, value)...]) if there is a match.  Otherwise,
        raise PatternMatchException().  This should be stateless.
        """
        pass

    def _match_value(self, matchee):
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


class ParallelMatcher(Matcher):

    def __init__(self, matcher1, matcher2):
        self.matcher1 = matcher1
        self.matcher2 = matcher2
        if not _vars_are_disjoint(util.flatten([matcher1.var_names(),
            matcher2.var_names()])):
            raise PatternVarConflict()

    def var_names(self):
        return util.flatten([self.matcher1.var_names(),
            self.matcher2.var_names()])

    def match(self, matchee):
        updates = []
        for matcher in [self.matcher1, self.matcher2]:
            match = matcher.match(matchee)
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


class WildcardMatcher(Matcher):
    
    def __init__(self):
        pass

    def var_names(self):
        return ['_']

    def match(self, matchee):
        return [('_', 3)]


class ClassMatcher(Matcher):

    def __init__(self, clazz, positionalMatchers, **kwMatchers):
        self.clazz = clazz
        self.positionalMatchers = positionalMatchers
        self.kwMatchers = kwMatchers

        # This stores which fields of the object we will need to look at.
        if not _vars_are_disjoint(util.flatten([m.var_names() for m in
            positionalMatchers + kwMatchers.values()])):
            raise PatternVarConflict()

    def var_names(self):
        return (util.flatten([matcher.var_names() 
            for matcher in self.positionalMatchers + self.kwMatchers.values()]))

    def default_unapply(self, matchee, kw_keys):
        if not isinstance(matchee, self.clazz):
            raise PatternMatchException("Matchee should be of type %r" %
                    (self.clazz,))
        pos_values = []
        kw_dict = {}

# We don't get the argspec unless there are actually positional matchers
        def genPosValues():
            arg_spec = inspect.getargspec(self.clazz.__init__)
            for arg in arg_spec.args:
                if arg != 'self':
                    yield(getattr(matchee, arg, None))
        pos_values = genPosValues()
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


def build_matcher(tree, modified):
    if isinstance(tree, Num):
        return hq[LiteralMatcher(u[tree.n])]
    if isinstance(tree, Str):
        return hq[LiteralMatcher(u[tree.s])]
    if isinstance(tree, Name):
        if tree.id in ['True', 'False', 'None']:
            return hq[LiteralMatcher(ast[tree])]
        elif tree.id in ['_']:
            return hq[WildcardMatcher()]
        modified.add(tree.id)
        return hq[NameMatcher(u[tree.id])]
    if isinstance(tree, List):
        sub_matchers = []
        for child in tree.elts:
            sub_matchers.append(build_matcher(child, modified))
        return Call(Name('ListMatcher', Load()), sub_matchers, [], None, None)
    if isinstance(tree, Tuple):
        sub_matchers = []
        for child in tree.elts:
            sub_matchers.append(build_matcher(child, modified))
        return Call(Name('TupleMatcher', Load()), sub_matchers, [], None, None)
    if isinstance(tree, Call):
        sub_matchers = []
        for child in tree.args:
            sub_matchers.append(build_matcher(child, modified))
        positional_matchers = List(sub_matchers, Load())
        kw_matchers = []
        for kw in tree.keywords:
            kw_matchers.append(
                    keyword(kw.arg, build_matcher(kw.value, modified)))
        return Call(Name('ClassMatcher', Load()), [tree.func,
            positional_matchers], kw_matchers, None, None)
    if (isinstance(tree, BinOp) and isinstance(tree.op, BitAnd)):
        sub1 = build_matcher(tree.left, modified)
        sub2 = build_matcher(tree.right, modified)
        return Call(Name('ParallelMatcher', Load()), [sub1, sub2], [], None,
                None)

    raise Exception("Unrecognized tree " + repr(tree))


def _is_pattern_match_stmt(tree):
    return (isinstance(tree, Expr) and
            _is_pattern_match_expr(tree.value))


def _is_pattern_match_expr(tree):
    return (isinstance(tree, BinOp) and
            isinstance(tree.op, LShift))


@macros.block
def _matching(tree, gen_sym, **kw):
    """
    This macro will enable non-refutable pattern matching.  If a pattern match
    fails, an exception will be thrown.
    """
    @Walker
    def func(tree, **kw):
        if _is_pattern_match_stmt(tree):
            modified = set()
            matcher = build_matcher(tree.value.left, modified)
            temp = gen_sym()
            # lol random names for hax
            with hq as assignment:
                name[temp] = ast[matcher]

            statements = [assignment, Expr(hq[name[temp]._match_value(ast[tree.value.right])])]

            for var_name in modified:
                statements.append(Assign([Name(var_name, Store())], hq[name[temp].get_var(u[var_name])]))

            return statements
        else:
            return tree

    func.recurse(tree)
    return [tree]


def _rewrite_if(tree, var_name=None, **kw_args):
    # TODO refactor into a _rewrite_switch and a _rewrite_if
    """
    Rewrite if statements to treat pattern matches as boolean expressions.

    Recall that normally a pattern match is a statement which will throw a
    PatternMatchException if the match fails.  We can therefore use try-blocks
    to produce the desired branching behavior.

    var_name is an optional parameter used for rewriting switch statements.  If
    present, it will transform predicates which are expressions into pattern
    matches.
    """

    # with q as rewritten:
    #     try:
    #         with matching:
    #             u%(matchPattern)
    #         u%(successBody)
    #     except PatternMatchException:
    #         u%(_maybe_rewrite_if(failBody))
    # return rewritten
    if not isinstance(tree, If):
        return tree

    if var_name:
        tree.test = BinOp(tree.test, LShift(), Name(var_name, Load()))
    elif not (isinstance(tree.test, BinOp) and isinstance(tree.test.op, LShift)):
        return tree      

    handler = ExceptHandler(hq[PatternMatchException], None, tree.orelse)
    try_stmt = TryExcept(tree.body, [handler], [])

    macroed_match = With(Name('_matching', Load()), None, [Expr(tree.test)])
    try_stmt.body = [macroed_match] + try_stmt.body

    if len(handler.body) == 1: # (== tree.orelse)
        # Might be an elif
        handler.body = [_rewrite_if(handler.body[0], var_name)]
    elif not handler.body:
        handler.body = [Pass()]

    return try_stmt


@macros.block
def switch(tree, args, gen_sym, **kw):
    """
    If supplied one argument x, switch will treat the predicates of any
    top-level if statements as patten matches against x.

    Pattern matches elsewhere are ignored.  The advantage of this is the
    limited reach ensures less interference with existing code.
    """
    new_id = gen_sym()
    for i in xrange(len(tree)):
        tree[i] = _rewrite_if(tree[i], new_id)
    tree = [Assign([Name(new_id, Store())], args[0])] + tree
    return tree


@macros.block
def patterns(tree, **kw):
    """
    This enables patterns everywhere!  NB if you use this macro, you will not be
    able to use real left shifts anywhere.
    """
    with q as new:
        with _matching:
            None

    new[0].body = Walker(lambda tree, **kw: _rewrite_if(tree)).recurse(tree)

    return new
