from sqlalchemy import *
import unittest

from macropy.macros2.linq import macros, sql

engine = create_engine("sqlite://")
for line in open("macros2/linq_test_dataset.sql").read().split(";"):
    engine.execute(line.strip())

metadata = MetaData(engine)
metadata.reflect()

bbc = Table('bbc', metadata, autoload=True)


def compare_queries(query1, query2):
    res1 = engine.execute(query1).fetchall()
    res2 = engine.execute(query2).fetchall()
    try:
        assert res1 == res2
    except Exception, e:
        print "FAILURE"
        print e
        print query1
        print res1
        print query2
        print res2
        raise e


class Tests(unittest.TestCase):
    """
    Most examples taken from
    http://sqlzoo.net/wiki/Main_Page
    """
    def test_basic(self):
        compare_queries(
            "SELECT name FROM bbc WHERE region = 'Europe'",
            sql%(x.name for x in bbc if x.region == 'Europe')
        )
        compare_queries(
            "SELECT name, area FROM bbc WHERE area > 10000000",
            sql%((x.name, x.area) for x in bbc if x.area > 10000000)
        )

    def test_nested(self):
        compare_queries(
            """
            SELECT name FROM bbc
            WHERE population > (
                SELECT population FROM bbc
                WHERE name='Russia'
            )
            """,
            sql%(
                x.name for x in bbc if x.population > (
                    y.population for y in bbc if y.name == 'Russia'
                )
            )
        )

        compare_queries(
            """
            SELECT name, region FROM bbc
            WHERE region IN (
                SELECT region FROM bbc
                WHERE name IN ('India', 'Iran')
            )
            """,
            sql%(
                (x.name, x.region) for x in bbc
                if x.region in (
                    y.region for y in bbc
                    if y.name in ['India', 'Iran']
                )
            )
        )
        compare_queries(
            """
            SELECT w.name, w.region
            FROM bbc w
            WHERE w.region in (
                SELECT z.region
                FROM bbc z
                WHERE z.name = 'Belize' OR z.name = 'Belgium'
            )
            """,
            sql%(
                (c.name, c.region) for c in bbc
                if c.region in (
                    x.region for x in bbc
                    if (x.name == 'Belize') | (x.name == 'Belgium')
                )
            )
        )

    def test_operators(self):
        compare_queries(
            """
            SELECT name FROM bbc
            WHERE gdp/population > (
                SELECT gdp/population FROM bbc
                WHERE name = 'United Kingdom'
            )
            AND region = 'Europe'
            """,
            sql%(
                x.name for x in bbc
                if x.gdp / x.population > (
                    y.gdp / y.population for y in bbc
                    if y.name == 'United Kingdom'
                )
                if (x.region == 'Europe')
            )
        )

    def test_aggregate(self):
        compare_queries(
            "SELECT SUM(population) FROM bbc",
            sql%(func.sum(x.population) for x in bbc)
        )
    def tsest_aliased(self):
        compare_queries(
            """
            SELECT DISTINCT(x.region)
            FROM bbc x
            WHERE 100000000 < (
                SELECT SUM(w.population)
                from bbc w
                WHERE w.region = x.region
            )
            """,
            sql%(
                func.distinct(x.region) for x in bbc
                if (
                    func.sum(w.population) for w in bbc
                    if w.region == x.region
                ) > 100000000
            )
        )
