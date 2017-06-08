# -*- coding: utf-8 -*-
"""Functions that are nice to have but really should be in the python
std lib.
"""


def flatten(xs):
    """Recursively flattens a list of lists of lists (arbitrarily,
    non-uniformly deep) into a single big list.
    """
    res = []

    def loop(ys):
        for i in ys:
            if isinstance(i, list):
                loop(i)
            elif i is None:
                pass
            else:
                res.append(i)
    loop(xs)
    return res


def singleton(cls):
    """Decorates a class to turn it into a singleton."""
    obj = cls()
    obj.__name__ = cls.__name__

    return obj


def merge_dicts(*my_dicts):
    """Combines a bunch of dictionaries together, later dictionaries taking
    precedence if there is a key conflict."""
    return dict((k, v) for d in my_dicts for (k, v) in d.items())


class Lazy(object):

    def __init__(self, thunk):
        self.thunk = thunk
        self.val = None

    def __call__(self):
        if self.val is None:
            self.val = [self.thunk()]
        return self.val[0]


def distinct(l):
    """Builds a new list with all duplicates removed."""
    s = []
    for i in l:
        if i not in s:
            s.append(i)
    return s


def register(array):
    """A decorator to add things to lists without stomping over its
    value."""
    def x(val):
        array.append(val)
        return val
    return x


def box(x):
    "None | T => [T]"
    return [x] if x else []
