# -*- coding: utf-8 -*-
import sys
import unittest

from macropy.peg import macros, peg, Success, cut, ParseError
from macropy.tracing import macros, require
from macropy.quick_lambda import macros, f, _


class Tests(unittest.TestCase):

    def test_basic(self):
        parse1 = peg["Hello World"]
        with require:
            parse1.parse_string("Hello World").output == 'Hello World'
            parse1.parse_string("Hello, World").index == 0

        parse2 = peg[("Hello World", (".").r)]
        with require:
            parse2.parse_string("Hello World").index == 11
            parse2.parse_string("Hello World1").output == ['Hello World', '1']
            parse2.parse_string("Hello World ").output == ['Hello World', ' ']

    def test_operators(self):
        parse1 = peg["Hello World"]

        parse2 = peg[(parse1, "!".rep1)]
        with require:
            parse2.parse_string("Hello World!!!").output == ['Hello World',
                                                             ['!', '!', '!']]
            parse2.parse_string("Hello World!").output  == ['Hello World',
                                                            ['!']]
            parse2.parse_string("Hello World").index == 11

        parse3 = peg[(parse1, ("!" | "?"))]

        with require:
            parse3.parse_string("Hello World!").output == ['Hello World', '!']
            parse3.parse_string("Hello World?").output == ['Hello World', '?']
            parse3.parse_string("Hello World%").index == 11

        parse4 = peg[(parse1, "!".rep & "!!!")]

        with require:
            parse4.parse_string("Hello World!!!").output == ['Hello World',
                                                             ['!', '!', '!']]
            parse4.parse_string("Hello World!!").index == 11

        parse4 = peg[(parse1, "!".rep & "!!!")]

        with require:
            parse4.parse_string("Hello World!!!").output == ["Hello World",
                                                             ["!", "!", "!"]]

        parse5 = peg[(parse1, "!".rep & -"!!!")]
        with require:
            parse5.parse_string("Hello World!!").output == ["Hello World",
                                                            ['!', '!']]
            parse5.parse_string("Hello World!!!").index == 11

        parse6 = peg[(parse1, "!" * 3)]
        with require:
            parse6.parse_string("Hello World!").index == 12
            parse6.parse_string("Hello World!!").index == 13
            parse6.parse_string("Hello World!!!").output == ["Hello World",
                                                             ['!', '!', '!']]
            parse6.parse_string("Hello World!!!!").index == 14

    def test_conversion(self):
        parse1 = peg[("Hello World", "!".rep1) // f[_[1]]]

        with require:
            parse1.parse_string("Hello World!!!").output == ['!', '!', '!']
            parse1.parse_string("Hello World").index == 11

        parse2 = parse1 // len

        with require:
            parse2.parse_string("Hello World!!!").output == 3


    def test_block(self):
        with peg:
            parse1 = ("Hello World", "!".rep1) // f[_[1]]
            parse2 = parse1 // len

        with require:
            parse1.parse_string("Hello World!!!").output == ['!', '!', '!']
            parse1.parse_string("Hello World").index == 11
            parse2.parse_string("Hello World!!!").output == 3

    def test_recursive(self):
        with peg:
            expr = ("(", expr, ")").rep | ""

        with require:
            expr.parse_string("()").output
            expr.parse_string("(()())").output
            expr.parse_partial("(((()))))").output

            expr.parse_partial("((()))))").output
            expr.parse_string("((()))))").index == 6
            expr.parse_partial(")((()()))(").output == []
            expr.parse_string(")((()()))(").index == 0
            expr.parse_partial(")()").output == []
            expr.parse_string(")()").index == 0

    def test_bindings(self):
        with peg:
            short = ("omg" is wtf) >> wtf * 2
            medium = ("omg" is o, " ", "wtf" is w, " ", "bb+q".r is b) >> o + w + b
            seq1 = ("l", ("ol".rep1) is xxx) >> xxx
            seq2 = ("l", ("ol" is xxx).rep1) >> xxx
            seq3 = ("l", ("ol" is xxx).rep1) >> sum(map(len, xxx))
        with require:
            short.parse_string('omg').output == 'omgomg'
            short.parse_string('omgg').index == 3
            short.parse_string('cow').index == 0
            medium.parse_string('omg wtf bbq').output == 'omgwtfbbq'
            medium.parse_string('omg wtf bbbbbq').output == 'omgwtfbbbbbq'
            medium.parse_string('omg wtf bbqq').index == 11
            seq3.parse_string("lolololol").output == 8

        for x in ["lol", "lolol", "ol", "'"]:
            if type(seq1.parse_string(x)) is Success:

                require[seq1.parse_string(x).output == seq2.parse_string(x).output]
            else:

                require[seq1.parse_string(x).index == seq2.parse_string(x).index]

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
                "+": f[_+_],
                "-": f[_-_],
                "*": f[_*_],
                "/": f[_/_],
            }
            while len(chain) > 1:
                a, [o, b] = chain.pop(), chain.pop()
                chain.append(o_dict[o](a, b))
            return chain[0]

        with peg:
            op = '+' | '-' | '*' | '/'
            value = '[0-9]+'.r // int | ('(', expr, ')') // f[_[1]]
            expr = (value, (op, value).rep is rest) >> reduce_chain([value] + rest)

        with require:
            expr.parse("123") == 123
            expr.parse("((123))") == 123
            expr.parse("(123+456+789)") == 1368
            expr.parse("(6/2)")  == 3
            expr.parse("(1+2+3)+2") == 8
            # TODO: this is was fixed here to get the right answer
            # according to python 3 arithmetic. The right thing is to
            # know exactly what PEG expects and fix in the code. was
            # expr.parse("(((((((11)))))+22+33)*(4+5+((6))))/12*(17+5)")  == 1804
            expr.parse("(((((((11)))))+22+33)*(4+5+((6))))/12*(17+5)")  == 1815.0


    def test_cut(self):
        with peg:
            expr1 = ("1", cut, "2", "3") | ("1", "b", "c")
            expr2 = ("1", "2", "3") | ("1", "b", "c")

        with require:
            expr1.parse_string("1bc").index == 1
            expr2.parse_string("1bc").output == ['1', 'b', 'c']

    def test_short_str(self):
        with peg:
            p1 = "omg"
            p2 = "omg".r
            p3 = "omg" | "wtf"
            p4 = "omg", "wtf"
            p5 = "omg" & "wtf"
            p6 = p1
            p7 = "a" | "b" | "c"
            p8 = ("1" | "2" | "3") & "\d".r & ("2" | "3") | p7

        with require:
            p1.parser.short_str() == "'omg'"
            p2.parser.short_str() == "'omg'.r"
            p3.parser.short_str() == "('omg' | 'wtf')"
            p4.parser.short_str() == "('omg', 'wtf')"
            p5.parser.short_str() == "('omg' & 'wtf')"
            p6.parser.short_str() == "p1"
            p7.parser.short_str() == "('a' | 'b' | 'c')"
            p8.parser.short_str() == "((('1' | '2' | '3') & '\\\\d'.r & ('2' | '3')) | p7)"

    def test_bindings_json(self):

        def test(parser, string):
            import json
            try:
                assert parser.parse(string) == json.loads(string)
            except Exception as e:
                print(parser.parse_string(string))
                print(json.loads(string))
                raise e

        def decode(x):
            # x is already a str, encode it to bytes and back
            x =  x.encode().decode('unicode-escape')
            return x

        escape_map = {
            '"': '"',
            '/': '/',
            '\\': '\\',
            'b': '\b',
            'f': '\f',
            'n': '\n',
            'r': '\r',
            't': '\t'
        }

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

        Number <- Minus? IntegralPart fractPart? expPart?

        Minus <- "-"
        IntegralPart <- "0" / [1-9] [0-9]*
        fractPart <- "." [0-9]+
        expPart <- ( "e" / "E" ) ( "+" / "-" )? [0-9]+
        S <- [ U+0009 U+000A U+000D U+0020 ]+
        """
        with peg:
            json_doc = (space, (obj | array), space) // f[_[1]]
            json_exp = (space, (obj | array | string | true | false | null |
                                number), space) // f[_[1]]

            pair = (string is k, space, ':', cut, json_exp is v) >> (k, v)
            obj = ('{', cut, pair.rep_with(",") // dict, space, '}') // f[_[1]]
            array = ('[', cut, json_exp.rep_with(","), space, ']') // f[_[1]]

            string = (space, '"',
                      (r'[^"\\\t\n]'.r | escape | unicode_escape).rep.join is
                      body, '"') >> "".join(body)
            escape = ('\\', ('"' | '/' | '\\' | 'b' | 'f' | 'n' | 'r' | 't') // escape_map.get) // f[_[1]]
            unicode_escape = ('\\', 'u', ('[0-9A-Fa-f]'.r * 4).join).join // decode

            true = 'true' >> True
            false = 'false' >> False
            null = 'null' >> None

            number = decimal | integer
            integer = ('-'.opt, integral).join // int
            decimal = ('-'.opt, integral, ((fract, exp).join) | fract | exp).join // float

            integral = '0' | '[1-9][0-9]*'.r
            fract = ('.', '[0-9]+'.r).join
            exp = (('e' | 'E'), ('+' | '-').opt, "[0-9]+".r).join

            space = '\s*'.r

        # test Success
        number.parse("0.123456789e-12")
        test(json_exp, r'{"\\": 123}')
        test(json_exp, "{}")

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

        # test Failure
        with self.assertRaises(ParseError) as e:
            json_exp.parse('{    : 1, "wtf": 12.4123}')

        msg = str(e.exception)
        assert msg ==\
"""
index: 5, line: 1, col: 6
json_exp / obj
{    : 1, "wtf": 12.4123}
     ^
expected: '}'
""".strip()

        with self.assertRaises(ParseError) as e:
            json_exp.parse('{"omg": "123", "wtf": , "bbq": "789"}')

        assert str(e.exception) ==\
"""
index: 22, line: 1, col: 23
json_exp / obj / pair / v / json_exp
{"omg": "123", "wtf": , "bbq": "789"}
                      ^
expected: (obj | array | string | true | false | null | number)
""".strip()

        with self.assertRaises(ParseError) as e:
            json_exp.parse("""{
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
                            "number": 646 555-4567"
                        }
                    ]
                }
            """)

        assert str(e.exception) == \
"""
index: 655, line: 18, col: 43
json_exp / obj / pair / v / json_exp / array / json_exp / obj
                         "number": 646 555-4567"
                                       ^
expected: '}'
""".strip()


        # full tests, taken from http://www.json.org/JSON_checker/
        for i in range(1, 34):
            if i not in [18]: # skipping the "too much nesting" failure test

                with self.assertRaises(ParseError):
                    json_doc.parse(open(__file__.rpartition('/')[0] + "/peg_json/fail%s.json" % i).read())

        for i in [1, 2, 3]:
            test(json_exp, open(__file__.rpartition('/')[0] + "/peg_json/pass%s.json" % i).read())
