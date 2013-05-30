import unittest
from macropy.core.util import singleton
from macropy.macros.adt import CaseClass


class Tests(unittest.TestCase):

    def test_nested(self):

        class List(CaseClass):

            def __len__(self):
                return 0

            def __iter__(self):
                return iter([])

            def __init__(self, *args, **kwargs):
                CaseClass.__init__(self, *args, **kwargs)
            _fields = []
            __slots__ = []

        @singleton
        def sym2():
            pass

            class Nil(List):

                def __init__(self, *args, **kwargs):
                    CaseClass.__init__(self, *args, **kwargs)
                    pass
                _fields = []
                __slots__ = []
            List.Nil = Nil

            class Cons(List):

                def __len__(self):
                    return (1 + len(self.tail))

                def __iter__(self):
                    current = self
                    while (len(current) > 0):
                        (yield current.head)
                        current = current.tail

                def __init__(self, *args, **kwargs):
                    CaseClass.__init__(self, *args, **kwargs)
                _fields = ['head', 'tail']
                __slots__ = ['head', 'tail']
            List.Cons = Cons

        assert isinstance(List.Cons(None, None), List)
        assert isinstance(List.Nil(), List)
        my_list = List.Cons(1, List.Cons(2, List.Cons(3, List.Nil())))
        empty_list = List.Nil()
        assert (len(my_list) == 3)
        assert (sum(iter(my_list)) == 6)
        assert (sum(iter(empty_list)) == 0)