from sqlalchemy import *
import unittest

from macropy.macros2.linq import macros, sql, generate_schema

engine = create_engine("sqlite://")
for line in open("macros2/linq_test_dataset.sql").read().split(";"):
    engine.execute(line.strip())

db = generate_schema(engine)

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
            sql%(x.name for x in db.bbc if x.region == 'Europe')
        )
        compare_queries(
            "SELECT name, area FROM bbc WHERE area > 10000000",
            sql%((x.name, x.area) for x in db.bbc if x.area > 10000000)
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
                x.name for x in db.bbc if x.population > (
                    y.population for y in db.bbc if y.name == 'Russia'
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
                (x.name, x.region) for x in db.bbc
                if x.region in (
                    y.region for y in db.bbc
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
                (c.name, c.region) for c in db.bbc
                if c.region in (
                    x.region for x in db.bbc
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
                x.name for x in db.bbc
                if x.gdp / x.population > (
                    y.gdp / y.population for y in db.bbc
                    if y.name == 'United Kingdom'
                )
                if (x.region == 'Europe')
            )
        )

    def test_aggregate(self):
        compare_queries(
            "SELECT SUM(population) FROM bbc",
            sql%(func.sum(x.population) for x in db.bbc)
        )

    def test_aliased(self):
        compare_queries(
            "select count(*) from bbc where area >= 1000000",
            sql%(func.count(x.name) for x in db.bbc if x.area >= 1000000)
        )
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
                func.distinct(x.region) for x in db.bbc
                if (
                    func.sum(w.population) for w in db.bbc
                    if w.region == x.region
                ) > 100000000
            )
        )

    def test_query_macro(self):
        query = sql%(
            func.distinct(x.region) for x in db.bbc
            if (
                func.sum(w.population) for w in db.bbc
                if w.region == x.region
            ) > 100000000
        )
        sql_results = engine.execute(query).fetchall()
        query_macro_results = query%(
            func.distinct(x.region) for x in db.bbc
            if (
                func.sum(w.population) for w in db.bbc
                if w.region == x.region
            ) > 100000000
        )
        assert sql_results == query_macro_results

    def test_join(self):
        compare_queries(
            """
            SELECT name
            FROM movie m
            JOIN actor a
            JOIN casting c
            WHERE m.title = 'Casablanca'
            AND m.id = c.movieid
            AND a.id = c.actorid
            """,
            sql%(
                a.name
                for m in db.movie
                for a in db.actor
                for c in db.casting
                if m.title == 'Casablanca'
                if m.id == c.movieid
                if a.id == c.actorid
            )
        )

        (
            """
            SELECT mm.title
            FROM movie mm
            JOIN actor aa
            JOIN casting cc
            WHERE mm.id = cc.movieid
            AND aa.id = cc.actorid
            AND mm.title IN (
                SELECT m.title
                FROM movie m
                JOIN actor a
                JOIN casting c
                WHERE m.id = c.movieid
                AND a.id = c.actorid
                AND a.name = 'Julie Andrews'
            )
            """
        )
