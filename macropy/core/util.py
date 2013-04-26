def flatten(xs):
    res = []
    def loop(ys):
        for i in ys:
            if isinstance(i, list): loop(i)
            elif i is None: pass
            else: res.append(i)
    loop(xs)
    return res


# Intended for use as a class decorator
def singleton(cls):
    return cls()


def type_dict(d):
    return lambda x: d[type(x)]