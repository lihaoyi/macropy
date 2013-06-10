"""Functions that are nice to have but really should be in the python library"""

def flatten(xs):
    """Recursively flattens a list of lists of lists (arbitrarily, non-uniformly
    deep) into a single big list."""
    res = []
    def loop(ys):
        for i in ys:
            if isinstance(i, list): loop(i)
            elif i is None: pass
            else: res.append(i)
    loop(xs)
    return res



def singleton(cls):
    """Decorates a class to turn it into a singleton."""
    obj = cls()
    obj.__name__ = cls.__name__
    return obj


def safe_splat(func, **kwargs):
    """Applies the function to the given kwargs, while taking special
    care not to give it too many arguments to cause TypeErrors. Extra arguments
    just get ignored."""
    import inspect
    fargs, fvarargs, fkwargs, fdefault = inspect.getargspec(func)


    cutkwargs = {k: w for k, w in kwargs.items() if k in fargs}

    return func(**cutkwargs)

def merge_dicts(my_dicts):
    """Combines a bunch of dictionaries together, later dictionaries taking
    precedence if there is a key conflict"""
    return dict((k,v) for d in my_dicts for (k,v) in d.items())

class Lazy:
    def __init__(self, thunk):
        self.thunk = thunk
        self.val = None
    def __call__(self):
        if self.val is None:
            self.val = [self.thunk()]
        return self.val[0]

def distinct(l):
    """Builds a new list with all duplicates removed"""
    s = []
    for i in l:
       if i not in s:
          s.append(i)
    return s