class Foo(object):
    __slots__ = ['x']
    def __init__(self, n):
        self.x = n

Foo.__slots__ = ['x']
y = Foo(1)
print y.x  # prints "1"
y.x = 2
print y.x  # prints "2"
y.z = 4    # Throws exception.
print y.z