class List:
    def __init__(self):
        print "list init"
    class Cons:
        def __init__(self, x, xs):
            self.x = x
            self.xs = xs


List.Cons = type("Cons", (object, List), List.Cons.__dict__)
List.Cons(1, 0)