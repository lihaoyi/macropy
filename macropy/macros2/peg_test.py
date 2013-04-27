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
            value = r('[0-9]+') * int | ('(', expr, ')') * (f%_[1])
            op = '+' | '-' | '*' | '/'
            expr = (value, ~(op, value)) ** (f%reduce_chain([_] + _))

        assert expr.parse_all("123") == [123]
        assert expr.parse_all("((123))") == [123]
        assert expr.parse_all("(123+456+789)") == [1368]
        assert expr.parse_all("(6/2)") == [3]
        assert expr.parse_all("(1+2+3)+2") == [8]
        assert expr.parse_all("(((((((11)))))+22+33)*(4+5+((6))))/12*(17+5)") == [1804]

    def test_json(self):
        """
        JSON <- S? ( Object / Array / String / True / False / Null / Number ) S?

        Object <- "{"
                     ( String ":" JSON ( "," String ":" JSON )*
                     / S? )
                 "}"

        Array <- "["
                    ( JSON ( "," JSON )*
                    / S? )
                "]"

        String <- S? ["] ( [^ " \ U+0000-U+001F ] / Escape )* ["] S?

        Escape <- [\] ( [ " / \ b f n r t ] / UnicodeEscape )

        UnicodeEscape <- "u" [0-9A-Fa-f]{4}

        True <- "true"
        False <- "false"
        Null <- "null"

        Number <- Minus? IntegralPart FractionalPart? ExponentPart?

        Minus <- "-"
        IntegralPart <- "0" / [1-9] [0-9]*
        FractionalPart <- "." [0-9]+
        ExponentPart <- ( "e" / "E" ) ( "+" / "-" )? [0-9]+
        S <- [ U+0009 U+000A U+000D U+0020 ]+

        """

        def test(parser, string):
            import json
            try:
                assert parser.parse_all(string)[0] == json.loads(string)
            except:
                print parser.parse_all(string)
                print json.loads(string)

        with peg:
            json_exp = (opt(space), (obj | array | string | true | false | null | number), opt(space)) * (lambda x: x[1])

            obj = ('{', ((string, ':', json_exp), ~((',', string, ':', json_exp) * (lambda x: [x[1], x[3]]))) | space, '}') * (
                lambda x: dict([[x[1][0][0], x[1][0][2]]] + [[y[0], y[1]] for y in x[1][1]])
            )
            array = ('[', (json_exp, ~(',', json_exp)) | space, ']') * (lambda x: [x[1][0]] + [y[1] for y in x[1][1]])

            string = (opt(space), '"', ~(r('[^"]') | escape) * ("".join), '"') * (f%"".join(_[2]))
            escape = '\\', ('"' | '/' | '\\' | 'b' | 'f' | 'n' | 'r' | 't' | unicode_escape)
            unicode_escape = 'u', +r('[0-9A-Fa-f]')

            true = 'true' * (lambda x: True)
            false = 'false' * (lambda x: False)
            null = 'null' * (lambda x: None)

            number = (opt(minus), integral, opt(fractional), opt(exponent)) ** (f%eval(_+_+_+_))
            minus = '-'
            integral = '0' | r('[1-9][0-9]*')
            fractional = ('.', r('[0-9]+')) ** (f%(_+_))
            exponent = (('e' | 'E'), opt('+' | '-'), r("[0-9]+")) ** (f%(_+_+_))

            space = r('\s+')

        test(number, "12031.33123E-2")
        test(string, '"i am a cow lol omfg"')
        test(array, '[1, 2, "omg", ["wtf", "bbq", 42]]')
        test(obj, '{"omg": "123", "wtf": 456, "bbq": "789"}')
        test(json_exp, '{"omg": 1, "wtf": 12.4123}  ')
        test(json_exp, """
            {
                "firstName": "John",
                "lastName": "Smith",
                "age": 25,
                "address": {
                    "streetAddress": "21 2nd Street",
                    "city": "New York",
                    "state": "NY",
                    "postalCode": 10021
                },
                "phoneNumbers": [
                    {
                        "type": "home",
                        "number": "212 555-1234"
                    },
                    {
                        "type": "fax",
                        "number": "646 555-4567"
                    }
                ]
            }
        """)