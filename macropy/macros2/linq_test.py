import unittest
import ast

from sqlalchemy import *
from macropy.macros2.linq import macros, sql, generate_schema
from macropy.core.lift import macros, q
from macropy.core import unparse_ast

engine = create_engine("sqlite://")

for line in open("macros2/world.sql").read().split(";"):
    engine.execute(line.strip())

db = generate_schema(engine)

def compare_queries(query1, query2, post_process=lambda x: x):
    res1 = engine.execute(query1).fetchall()
    res2 = engine.execute(query2).fetchall()
    try:
        assert post_process(res1) == post_process(res2)
    except Exception, e:
        print "FAILURE"
        print e
        print query1
        print "\n".join(map(str, post_process(res1)))
        print query2
        print "\n".join(map(str, post_process(res2)))
        raise e

class Tests(unittest.TestCase):

    def test_expand_lets(self):
        """
        This tests the sorta knotty logic involved in making the for-
        comprehension variable available *outside* of the comprehension
        when used in PINQ
        """
        tree = q%(lambda x: x + (lambda y: y + 1)(3))(5)
        goal = q%(lambda x: (lambda y: (x + (y + 1)))(3))(5)

        new_tree = replace_walk.recurse(tree)
        assert ast.dump(new_tree) == ast.dump(goal)

        tree = q%(lambda x: x + (lambda y: y + 1)(3) + (lambda z: z + 2)(4))(5)
        goal = q%(lambda x: (lambda z: (lambda y: ((x + (y + 1)) + (z + 2)))(3))(4))(5)

        new_tree = replace_walk.recurse(tree)
        assert ast.dump(new_tree) == ast.dump(goal)

        tree = q%(lambda x: (x, lambda w: (lambda y: y + 1)(3) + (lambda z: z + 2)(4)))(5)
        goal = q%(lambda x: (x, (lambda w: (lambda z: (lambda y: ((y + 1) + (z + 2)))(3))(4))))(5)

        new_tree = replace_walk.recurse(tree)
        assert ast.dump(new_tree) == ast.dump(goal)
    """
    Most examples taken from
    http://sqlzoo.net/wiki/Main_Page
    """
    def test_basic(self):
        # all countries in europe
        compare_queries(
            "SELECT name FROM country WHERE continent = 'Europe'",
            sql%(x.name for x in db.country if x.continent == 'Europe')
        )
        # countries whose area is bigger than 10000000
        compare_queries(
            "SELECT name, surface_area FROM country WHERE surface_area > 10000000",
            sql%((x.name, x.surface_area) for x in db.country if x.surface_area > 10000000)
        )
