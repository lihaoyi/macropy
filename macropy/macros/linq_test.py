import unittest

from macropy.core.macros import *
from macropy.core.lift import *
from macropy.macros.string_interp import *
import time

class Tests(unittest.TestCase):
    def test_basic(self):
        import sqlite3
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        for line in open("linq_test_dataset.sql").read().split(";"):
            cursor.execute(line.strip())

        conn.commit()

        def rawQuery(string):
            cursor = conn.cursor()
            cursor.execute(string)
            return cursor.fetchall()



        dbA = []
        dbB = []
        print rawQuery("""SELECT name FROM bbc""")
        sql%(x.foo for x in dbA)

        print rawQuery("""SELECT name FROM bbc WHERE region = 'Europe'""")
        sql%(x for x in dbA if x > 5)

        print rawQuery(
            """
            SELECT region, name, population FROM bbc x
            WHERE population >= (
                SELECT MAX(population) FROM bbc y
                WHERE y.region=x.region
                AND population>0
            )
            """
        )

        sql%(
            (x.region, x.name, x.population)
            for x in bbc
            if x.population >= max(
                y.population
                for y in bbc
                if y.region == x.region
                and y.population > 0
            )
        )
