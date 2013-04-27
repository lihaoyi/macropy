import unittest
from macropy.macros2.peg import macros
from macropy.macros2.peg import *

class Tests(unittest.TestCase):
    def test_basic(self):
        parse1 = peg%"Hello World"
        assert parse1.parse("Hello World")[0] == 'Hello World'
        assert parse1.parse("Hello, World") is None

        parse2 = peg%("Hello World", r("."))
        assert parse2.parse("Hello World") is None
        assert parse2.parse("Hello World1")[0] == ['Hello World', '1']
        assert parse2.parse("Hello World ")[0] == ['Hello World', ' ']

    def test_operators(self):
        parse1 = peg%"Hello World"

        parse2 = peg%(parse1, +"!")
        assert parse2.parse("Hello World!!!")[0] == ['Hello World', ['!', '!', '!']]
        assert parse2.parse("Hello World!")[0] == ['Hello World', ['!']]
        assert parse2.parse("Hello World") is None

        parse3 = peg%(parse1, ("!" | "?"))
        assert parse3.parse("Hello World!")[0] == ['Hello World', '!']
        assert parse3.parse("Hello World?")[0] == ['Hello World', '?']
        assert parse3.parse("Hello World%") is None

        parse4 = peg%(parse1, ~"!" & "!!!")
        assert parse4.parse("Hello World!!!")[0] == ['Hello World', ['!', '!', '!']]
        assert parse4.parse("Hello World!!") is None

        parse4 = peg%(parse1, ~"!" & "!!!")
        assert parse4.parse("Hello World!!!")[0] == ["Hello World", ["!", "!", "!"]]

        parse5 = peg%(parse1, ~"!" & -"!!!")
        assert parse5.parse("Hello World!!")[0] == ["Hello World", ['!', '!']]
        assert parse5.parse("Hello World!!!") is None

