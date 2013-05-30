import unittest
import macropy.core.macros


runner = unittest.TextTestRunner()
def run(x):
    runner.run(unittest.TestLoader().loadTestsFromTestCase(x))


from macropy.macros import adt_test
run(adt_test.Tests)

# this one creates a sqlite database to run, so may take a while
# from macropy.macros2 import linq_test
# run(linq_test.Tests)

# this one needs chromedriver in order to run the javascript using Selenium
#from macropy.macros2 import javascript_test
#run(javascript_test.Tests)
