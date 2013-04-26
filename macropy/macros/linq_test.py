import unittest
import sqlite3

import time
from macropy.macros.linq import macros, sql


conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

for line in open("macros/linq_test_dataset.sql").read().split(";"):
    cursor.execute(line.strip())

conn.commit()

def raw_query(string):
    cursor = conn.cursor()
    cursor.execute(string)
    return cursor.fetchall()

def compare_queries(query1, query2):
    try:
        res1 = raw_query(query1)
        res2 = raw_query(query2)
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
                    y.population for y in bbc if name == 'Russia'
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
                ) and x.region == 'Europe'
            )
        )

    def test_aggregate(self):
        """
        print raw_query("SELECT SUM(population) FROM bbc")
        print sql%sum(x.population for x in bbc)
        """