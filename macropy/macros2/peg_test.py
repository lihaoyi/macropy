import unittest
from macropy.macros2.peg import macros
from macropy.macros2.peg import *
from macropy.macros.quicklambda import macros, f, _
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


    def test_conversion(self):
        parse1 = peg%(("Hello World", +"!") ** (lambda _, x: x))

        assert parse1.parse("Hello World!!!")[0] == ['!', '!', '!']
        assert parse1.parse("Hello World") is None

        parse2 = parse1 * len
        assert parse2.parse("Hello World!!!")[0] == 3


    def test_block(self):
        with peg:
            parse1 = ("Hello World", +"!") ** (lambda _, x: x)
            parse2 = parse1 * len

        assert parse1.parse("Hello World!!!")[0] == ['!', '!', '!']
        assert parse1.parse("Hello World") is None
        assert parse2.parse("Hello World!!!")[0] == 3

    def test_recursive(self):
        with peg:
            expr = ~("(", expr, ")") | ""

        assert expr.parse("()") is not None
        assert expr.parse("(()())") is not None
        assert expr.parse("(((()))))") is not None

        assert expr.parse("((()))))") is not None
        assert expr.parse_all("((()))))") is None
        assert expr.parse(")((()()))(") is not None
        assert expr.parse_all(")((()()))(") is None
        assert expr.parse(")()") is not None
        assert expr.parse_all(")()") is None

    def test_arithmetic(self):
        """
        PEG grammar from Wikipedia

        Op      <- "+" / "-" / "*" / "/"
        Value   <- [0-9]+ / '(' Expr ')'
        Expr <- Value (Op Value)*

        simplified it to remove operator precedence
        """

        def reduce_chain(chain):
            chain = list(reversed(chain))
            o_dict = {
                "+": f%(_+_),
                "-": f%(_-_),
                "*": f%(_*_),
                "/": f%(_/_),
            }
            while len(chain) > 1:
                a, [o, b] = chain.pop(), chain.pop()
                chain.append(o_dict[o](a, b))
            return chain[0]

        with peg:
            value = r('\d+') * int | ('(', expr, ')') * (f%_[1])
            op = '+' | '-' | '*' | '/'
            expr = (value, ~(op, value)) ** (f%reduce_chain([_] + _))

        assert expr.parse_all("123") == [123]
        assert expr.parse_all("((123))") == [123]
        assert expr.parse_all("(123+456+789)") == [1368]
        assert expr.parse_all("(6/2)") == [3]
        assert expr.parse_all("(1+2+3)+2") == [8]
        assert expr.parse_all("(((((((11)))))+22+33)*(4+5+((6))))/12*(17+5)") == [1804]

