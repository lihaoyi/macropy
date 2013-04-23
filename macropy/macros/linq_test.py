import unittest
import sqlite3
from macropy.core.macros import *
from macropy.core.lift import *
from macropy.macros.string_interp import *
import time
from linq import *


conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

for line in open("macros/linq_test_dataset.sql").read().split(";"):
    cursor.execute(line.strip())

conn.commit()

def rawQuery(string):
    cursor = conn.cursor()
    cursor.execute(string)
    return cursor.fetchall()

def compareResults(query1, query2):
    assert rawQuery(query1) == rawQuery(query2)

class Tests(unittest.TestCase):
    def test_basic(self):
        compareResults(
            "SELECT name FROM bbc WHERE region = 'Europe'",
            sql%(x.name for x in bbc if x.region == 'Europe')
        )


