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

        new_tree = expand_let_bindings.recurse(tree)
        assert ast.dump(new_tree) == ast.dump(goal)

        tree = q%(lambda x: x + (lambda y: y + 1)(3) + (lambda z: z + 2)(4))(5)
        goal = q%(lambda x: (lambda z: (lambda y: ((x + (y + 1)) + (z + 2)))(3))(4))(5)

        new_tree = expand_let_bindings.recurse(tree)
        assert ast.dump(new_tree) == ast.dump(goal)

        tree = q%(lambda x: (x, lambda w: (lambda y: y + 1)(3) + (lambda z: z + 2)(4)))(5)
        goal = q%(lambda x: (x, (lambda w: (lambda z: (lambda y: ((y + 1) + (z + 2)))(3))(4))))(5)

        new_tree = expand_let_bindings.recurse(tree)
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

    def test_nested(self):

        # countries on the same continent as India or Iran
        compare_queries(
            """
            SELECT name, continent FROM country
            WHERE continent IN (
                SELECT continent FROM country
                WHERE name IN ('India', 'Iran')
            )
            """,
            sql%(
                (x.name, x.continent) for x in db.country
                if x.continent in (
                    y.continent for y in db.country
                    if y.name in ['India', 'Iran']
                )
            )
        )

        # countries in the same continent as Belize or Belgium
        compare_queries(
            """
            SELECT w.name, w.continent
            FROM country w
            WHERE w.continent in (
                SELECT z.continent
                FROM country z
                WHERE z.name = 'Belize' OR z.name = 'Belgium'
            )
            """,
            sql%(
                (c.name, c.continent) for c in db.country
                if c.continent in (
                    x.continent for x in db.country
                    if (x.name == 'Belize') | (x.name == 'Belgium')
                )
            )
        )

    def test_operators(self):
        # countries in europe with a DNP per capita larger than the UK
        compare_queries(
            """
            SELECT name FROM country
            WHERE gnp/population > (
                SELECT gnp/population FROM country
                WHERE name = 'United Kingdom'
            )
            AND continent = 'Europe'
            """,
            sql%(
                x.name for x in db.country
                if x.gnp / x.population > (
                    y.gnp / y.population for y in db.country
                    if y.name == 'United Kingdom'
                )
                if (x.continent == 'Europe')
            )
        )

    def test_aggregate(self):
        # the population of the world
        compare_queries(
            "SELECT SUM(population) FROM country",
            sql%(func.sum(x.population) for x in db.country)
        )
        # number of countries whose area is at least 1000000
        compare_queries(
            "select count(*) from country where surface_area >= 1000000",
            sql%(func.count(x.name) for x in db.country if x.surface_area >= 1000000)
        )

    def test_aliased(self):

        # continents whose total population is greater than 100000000
        compare_queries(
            """
            SELECT DISTINCT(x.continent)
            FROM country x
            WHERE 100000000 < (
                SELECT SUM(w.population)
                from country w
                WHERE w.continent = x.continent
            )
            """,
            sql%(
                func.distinct(x.continent) for x in db.country
                if (
                    func.sum(w.population) for w in db.country
                    if w.continent == x.continent
                ).as_scalar() > 100000000
            )
        )

    def test_query_macro(self):
        query = sql%(
            func.distinct(x.continent) for x in db.country
            if (
                func.sum(w.population) for w in db.country
                if w.continent == x.continent
            ) > 100000000
        )
        sql_results = engine.execute(query).fetchall()
        query_macro_results = query%(
            func.distinct(x.continent) for x in db.country
            if (
                func.sum(w.population) for w in db.country
                if w.continent == x.continent
            ) > 100000000
        )
        assert sql_results == query_macro_results


    def test_join(self):
        # number of cities in Asia
        compare_queries(
            """
            SELECT COUNT(t.name)
            FROM country c
            JOIN city t
            ON (t.country_code = c.code)
            WHERE c.continent = 'Asia'
            """,
            sql%(
                func.count(t.name)
                for c in db.country
                for t in db.city
                if t.country_code == c.code
                if c.continent == 'Asia'
            )
        )

        # name and population for each country and city where the city's
        # population is more than half the country's
        compare_queries(
            """
            SELECT t.name, t.population, c.name, c.population
            FROM country c
            JOIN city t
            ON t.country_code = c.code
            WHERE t.population > c.population / 2
            """,
            sql%(
                (t.name, t.population, c.name, c.population)
                for c in db.country
                for t in db.city
                if t.country_code == c.code
                if t.population > c.population / 2
            ),
            lambda x: sorted(map(str, x))
        )
    def test_join_complicated(self):
        compare_queries(
            """
            SELECT t.name, t.population, c.name, c.population
            FROM country c
            JOIN city t
            ON t.country_code = c.code
            AND t.population * 1.0 / c.population = (
                SELECT MAX(tt.population * 1.0 / c.population)
                FROM city tt
                WHERE tt.country_code = t.country_code
            )
            """,
            sql%(
                (t.name, t.population, c.name, c.population)
                for c in db.country
                for t in db.city
                if t.country_code == c.code
                if t.population * 1.0 / c.population == (
                    func.max(tt.population * 1.0 / c.population)
                    for tt in db.city
                    if tt.country_code == t.country_code
                )
            ),
            lambda x: sorted(map(str, x))
        )

    def test_order_group(self):
        # the name of every country sorted in order
        compare_queries(
            "SELECT c.name FROM country c ORDER BY c.population",
            sql%(c.name for c in db.country).order_by(c.population)
        )

        # sum up the population of every country using GROUP BY instead of a JOIN
        compare_queries(
            """
            SELECT t.country_code, sum(t.population)
            FROM city t GROUP BY t.country_code
            ORDER BY sum(t.population)
            """,
            sql%(
                (t.country_code, func.sum(t.population)) for t in db.city
            ).group_by(t.country_code)
             .order_by(func.sum(t.population))
        )

    def test_limit_offset(self):
        # bottom 10 countries by population
        compare_queries(
            "SELECT c.name FROM country c ORDER BY c.population LIMIT 10",
            sql%(c.name for c in db.country).order_by(c.population).limit(10)
        )

        # bottom 100 to 110 countries by population
        compare_queries(
            "SELECT c.name FROM country c ORDER BY c.population LIMIT 10 OFFSET 100",
            sql%(c.name for c in db.country).order_by(c.population).limit(10).offset(100)
        )

        # top 10 countries by population
        compare_queries(
            "SELECT c.name FROM country c ORDER BY c.population DESC LIMIT 10",
            sql%(c.name for c in db.country).order_by(c.population.desc()).limit(10)
        )


