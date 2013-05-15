import unittest
import ast
from macropy.macros2.javascript import macros, js, std_lib_script
import pjs

from selenium import webdriver

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
    @classmethod
    def tearDownClass(cls):
        cls.driver.close()

    def exec_js(self, script):
        return Tests.driver.execute_script(
            std_lib_script + "return " + script
        )

    def exec_js_func(self, script, *args):
        arg_list = ", ".join("arguments[%s]" % i for i in range(len(args)))
        return Tests.driver.execute_script(
            std_lib_script + "return (" + script + ")(%s)" % arg_list,
            *args
        )
    def test_literals(self):
        # these work
        assert self.exec_js(js%10) == 10
        assert self.exec_js(js%"i am a cow") == "i am a cow"

        # these literals are buggy, and it seems to be PJs' fault
        # ??? all the results seem to turn into strings ???
        assert self.exec_js(js%3.14) == str(3.14)
        assert self.exec_js(js%[1, 2, 'lol']) == str([1, 2, 'lol'])
        assert self.exec_js(js%{"moo": 2, "cow": 1}) == str({"moo": 2, "cow": 1})

        # set literals don't work so this throws an exception at macro-expansion time
        #self.exec_js(js%{1, 2, 'lol'})

    def test_executions(self):
        assert self.exec_js(js%(lambda x: x * 2)(10)) == 20
        assert self.exec_js(js%sum([x for x in range(10) if x > 5])) == 30

    def test_pyjs(self):
        code, javascript = pyjs%(lambda x: x > 5 and x % 2 == 0)
        print code
        for i in range(10):
            print i, code(i), self.exec_js_func(javascript, i)


        print self.exec_js(js%[y for x in range(5) for y in range(x)])