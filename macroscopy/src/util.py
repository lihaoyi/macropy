def flatten(xs):
    res = []
    def loop(ys):
        for i in ys:
            if isinstance(i, list): loop(i)
            elif i is None: pass
            else: res.append(i)
    loop(xs)
    return res


def singleton(cls):
    return cls()