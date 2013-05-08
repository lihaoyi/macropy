import unittest
from macropy.macros2.peg import macros

from macropy.macros.quicklambda import macros, f, _
class Tests(unittest.TestCase):
    def test_basic(self):
        parse1 = peg%"Hello World"

        assert parse1.parse_all("Hello World")[0] == 'Hello World'
        assert parse1.parse_all("Hello, World") is None

        parse2 = peg%("Hello World", (".").r)
        assert parse2.parse_all("Hello World") is None
        assert parse2.parse_all("Hello World1")[0] == ['Hello World', '1']
        assert parse2.parse_all("Hello World ")[0] == ['Hello World', ' ']

    def test_operators(self):
        parse1 = peg%"Hello World"

        parse2 = peg%(parse1, "!".rep1)
        assert parse2.parse_all("Hello World!!!")[0] == ['Hello World', ['!', '!', '!']]
        assert parse2.parse_all("Hello World!")[0] == ['Hello World', ['!']]
        assert parse2.parse_all("Hello World") is None

        parse3 = peg%(parse1, ("!" | "?"))
        assert parse3.parse_all("Hello World!")[0] == ['Hello World', '!']
        assert parse3.parse_all("Hello World?")[0] == ['Hello World', '?']
        assert parse3.parse_all("Hello World%") is None

        parse4 = peg%(parse1, "!".rep & "!!!")
        assert parse4.parse_all("Hello World!!!")[0] == ['Hello World', ['!', '!', '!']]
        assert parse4.parse_all("Hello World!!") is None

        parse4 = peg%(parse1, "!".rep & "!!!")
        assert parse4.parse_all("Hello World!!!")[0] == ["Hello World", ["!", "!", "!"]]

        parse5 = peg%(parse1, "!".rep & -"!!!")
        assert parse5.parse_all("Hello World!!")[0] == ["Hello World", ['!', '!']]
        assert parse5.parse_all("Hello World!!!") is None

        parse6 = peg%(parse1, "!" * 3)
        assert parse6.parse_all("Hello World!") is None
        assert parse6.parse_all("Hello World!!") is None
        assert parse6.parse_all("Hello World!!!")[0] == ["Hello World", ['!', '!', '!']]
        assert parse6.parse_all("Hello World!!!!") is None


    def test_conversion(self):
        parse1 = peg%(("Hello World", "!".rep1) // (f%_[1]))

        assert parse1.parse("Hello World!!!")[0] == ['!', '!', '!']
        assert parse1.parse("Hello World") is None

        parse2 = parse1 // len
        assert parse2.parse("Hello World!!!")[0] == 3


    def test_block(self):
        with peg:
            parse1 = ("Hello World", "!".rep1) // (f%_[1])
            parse2 = parse1 // len

        assert parse1.parse("Hello World!!!")[0] == ['!', '!', '!']
        assert parse1.parse("Hello World") is None
        assert parse2.parse("Hello World!!!")[0] == 3

    def test_recursive(self):
        with peg:
            expr = ("(", expr, ")").rep | ""

        assert expr.parse("()") is not None
        assert expr.parse("(()())") is not None
        assert expr.parse("(((()))))") is not None

        assert expr.parse("((()))))") is not None
        assert expr.parse_all("((()))))") is None
        assert expr.parse(")((()()))(") is not None
        assert expr.parse_all(")((()()))(") is None
        assert expr.parse(")()") is not None
        assert expr.parse_all(")()") is None

    def test_bindings(self):
        with peg:
            short = ("omg" is wtf) >> wtf * 2
            medium = ("omg" is o, " ", "wtf" is w, " ", "bb+q".r is b) >> o + w + b
            seq1 = ("l", ("ol".rep1) is xxx) >> xxx
            seq2 = ("l", ("ol" is xxx).rep1) >> xxx
            seq3 = ("l", ("ol" is xxx).rep1) >> sum(map(len, xxx))

        assert short.parse_all('omg') == ['omgomg']
        assert short.parse_all('omgg') is None
        assert short.parse_all('cow') is None
        assert medium.parse_all('omg wtf bbq') == ['omgwtfbbq']
        assert medium.parse_all('omg wtf bbbbbq') == ['omgwtfbbbbbq']
        assert medium.parse_all('omg wtf bbqq') is None
        for x in ["lol", "lolol", "ol", "'"]:
            assert seq1.parse_all(x) == seq2.parse_all(x)

        assert seq3.parse_all("lolololol") == [8]

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
            value = '[0-9]+'.r // int | ('(', expr, ')') // (f%_[1])
            op = '+' | '-' | '*' | '/'
            expr = (value is first, (op, value).rep is rest) >> reduce_chain([first] + rest)


        assert expr.parse_all("123") == [123]
        assert expr.parse_all("((123))") == [123]
        assert expr.parse_all("(123+456+789)") == [1368]
        assert expr.parse_all("(6/2)") == [3]
        assert expr.parse_all("(1+2+3)+2") == [8]
        assert expr.parse_all("(((((((11)))))+22+33)*(4+5+((6))))/12*(17+5)") == [1804]



    def test_bindings_json(self):

        def test(parser, string):
            import json
            try:
                assert parser.parse_all(string)[0] == json.loads(string)
            except Exception, e:
                print parser.parse_all(string)
                print json.loads(string)
                raise e
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
        with peg:
            json_exp = (space.opt, (obj | array | string | true | false | null | number) is exp, space.opt) >> exp

            pair = (string is k, ':', json_exp is v) >> (k, v)
            obj = ('{', pair is first, (',', pair is rest).rep, space.opt, '}') >> dict([first] + rest)
            array = ('[', json_exp is first, (',', json_exp is rest).rep, space.opt, ']') >> [first] + rest

            string = (space.opt, '"', ('[^"]'.r | escape).rep // ("".join) is body, '"') >> "".join(body)
            escape = '\\', ('"' | '/' | '\\' | 'b' | 'f' | 'n' | 'r' | 't' | unicode_escape)
            unicode_escape = 'u', '[0-9A-Fa-f]'.r * 4

            true = 'true' >> True
            false = 'false' >> False
            null = 'null' >> None

            number = (minus.opt, integral, fractional.opt, exponent.opt) // (f%float("".join(_)))
            minus = '-'
            integral = '0' | '[1-9][0-9]*'.r
            fractional = ('.', '[0-9]+'.r) // "".join
            exponent = (('e' | 'E'), ('+' | '-').opt, "[0-9]+".r) // "".join

            space = '\s+'.r

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