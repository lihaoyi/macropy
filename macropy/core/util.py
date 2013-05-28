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
    return cls()


def safe_splat(func, **kwargs):
    """Applies the function to the given kwargs, while taking special
    care not to give it too many arguments to cause TypeErrors. Extra arguments
    just get ignored."""
    import inspect
    fargs, fvarargs, fkwargs, fdefault = inspect.getargspec(func)


    cutkwargs = {k: w for k, w in kwargs.items() if k in fargs}

    return func(**cutkwargs)