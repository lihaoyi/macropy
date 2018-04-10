.. _pinq:

PINQ to SQLAlchemy
------------------

.. code:: python

  from macropy.experimental.pinq import macros, sql, query, generate_schema
  from sqlalchemy import *

  # prepare database
  engine = create_engine("sqlite://")
  for line in open("macropy/experimental/test/world.sql").read().split(";"):
      engine.execute(line.strip())

  db = generate_schema(engine)

  # Countries in Europe with a GNP per Capita greater than the UK
  results = query[(
      x.name for x in db.country
      if x.gnp / x.population > (
          y.gnp / y.population for y in db.country
          if y.name == 'United Kingdom'
      ).as_scalar()
      if (x.continent == 'Europe')
  )]
  for line in results: print(line)
  # (u'Austria',)
  # (u'Belgium',)
  # (u'Switzerland',)
  # (u'Germany',)
  # (u'Denmark',)
  # (u'Finland',)
  # (u'France',)
  # (u'Iceland',)
  # (u'Liechtenstein',)
  # (u'Luxembourg',)
  # (u'Netherlands',)
  # (u'Norway',)
  # (u'Sweden',)


PINQ (Python INtegrated Query) to SQLAlchemy is inspired by `C#'s LINQ
to SQL <http://msdn.microsoft.com/en-us/library/bb386976.aspx>`_. In
short, code used to manipulate lists is lifted into an AST which is
then cross-compiled into a snippet of `SQL
<http://en.wikipedia.org/wiki/SQL>`_. In this case, it is the ``query``
macro which does this lifting and cross-compilation. Instead of
performing the manipulation locally on some data structure, the
compiled query is sent to a remote database to be performed there.

This allows you to write queries to a database in the same way you
would write queries on in-memory lists, which is really very nice. The
translation is a relatively thin layer of over the `SQLAlchemy Query
Language <http://docs.sqlalchemy.org/ru/latest/core/tutorial.html>`_,
which does the heavy lifting of converting the query into a raw SQL
string:. If we start with a simple query:

.. code:: python

  # Countries with a land area greater than 10 million square kilometers
  print(query[((x.name, x.surface_area) for x in db.country if x.surface_area > 10000000)])
  # [(u'Antarctica', Decimal('13120000.0000000000')), (u'Russian Federation', Decimal('17075400.0000000000'))]


This is to the equivalent SQLAlchemy query:

.. code:: python

  print(engine.execute(select([country.c.name, country.c.surface_area]).where(country.c.surface_area > 10000000)).fetchall())


To verify that PINQ is actually cross-compiling the python to SQL, and
not simply requesting everything and performing the manipulation
locally, we can use the ``sql`` macro to perform the lifting of the
query without executing it:

.. code:: python

  query_string = sql[((x.name, x.surface_area) for x in db.country if x.surface_area > 10000000)]
  print(type(query_string))
  # <class 'sqlalchemy.sql.expression.Select'>
  print(query_string)
  # SELECT country_1.name, country_1.surface_area
  # FROM country AS country_1
  # WHERE country_1.surface_area > ?

As we can see, PINQ converts the python list-comprehension into a
SQLAlchemy ``Select``, which when stringified becomes a valid SQL
string. The ``?``  are there because SQLAlchemy uses `parametrized
queries`__, and
doesn't interpolate values into the query itself.

__ http://en.wikipedia.org/wiki/Prepared_statement

Consider a less trivial example: we want to find all countries in
europe who have a `GNP per Capita`__ greater than
the United Kingdom. This is the SQLAlchemy code to do so:

__ http://en.wikipedia.org/wiki/Gross_national_product

.. code:: python

  query = select([db.country.c.name]).where(
      db.country.c.gnp / db.country.c.population > select(
          [(db.country.c.gnp / db.country.c.population)]
      ).where(
              db.country.c.name == 'United Kingdom'
      ).as_scalar()
  ).where(
      db.country.c.continent == 'Europe'
  )


The SQLAlchemy query looks pretty odd, for somebody who knows python
but isn't familiar with the library. This is because SQLAlchemy cannot
"lift" Python code into an AST to manipulate, and instead have to
construct the AST manually using python objects. Although it works
pretty well, the syntax and semantics of the queries is completely
different from python.

Already we are bumping into edge cases: the ``db.country`` in the nested
query is referred to the same way as the ``db.country`` in the outer
query, although they are clearly different! One may wonder, what if,
in the inner query, we wish to refer to the outer query's values?
Naturally, there will be solutions to all of these requirements. In
the end, SQLAlchemy ends up effectively creating its own mini
programming language, with its own concept of scoping, name binding,
etc., basically duplicating what Python already has but with messier
syntax and subtly different semantics.

In the equivalent PINQ code, the scoping of which ``db.country`` you are
referring to is much more explicit, and in general the semantics are
identical to a typical python comprehension:

.. code:: python

  query = sql[(
      x.name for x in db.country
      if x.gnp / x.population > (
          y.gnp / y.population for y in db.country
          if y.name == 'United Kingdom'
      ).as_scalar()
      if (x.continent == 'Europe')
  )]


As we can see, rather than mysteriously referring to the ``db.country``
all over the place, we clearly bind it in two places: once to the
variable ``x`` in the outer query, once to the variable ``y`` in the inner
query. Overall, we make use of Python's syntax and semantics (scoping,
names, etc.) rather than having to re-invent our own, which is a big
win for anybody who already understands Python.

Executing either of these will give us the same answer:

.. code:: python

  print(query)
  # SELECT country_1.name
  # FROM country AS country_1
  # WHERE country_1.gnp / country_1.population > (SELECT country_2.gnp / country_2.population AS anon_1
  # FROM country AS country_2
  # WHERE country_2.name = ?) AND country_1.continent = ?

  results = engine.execute(query).fetchall()

  for line in results: print(line)
  # (u'Austria',)
  # (u'Belgium',)
  # (u'Switzerland',)
  # (u'Germany',)
  # (u'Denmark',)
  # (u'Finland',)
  # (u'France',)
  # (u'Iceland',)
  # (u'Liechtenstein',)
  # (u'Luxembourg',)
  # (u'Netherlands',)
  # (u'Norway',)
  # (u'Sweden',)


Although PINQ does not support the vast capabilities of the SQL
language, it supports a useful subset, like ``JOINs``:

.. code:: python

  # The number of cities in all of Asia
  query = sql[(
      func.count(t.name)
      for c in db.country
      for t in db.city
      if t.country_code == c.code
      if c.continent == 'Asia'
  )]
  print(query)
  # SELECT count(city_1.name) AS count_1
  # FROM city AS city_1, country AS country_1
  # WHERE city_1.country_code = country_1.code AND country_1.continent = ?

  result = engine.execute(query).fetchall()

  print(result)
  [(1766,)]


As well as ``ORDER BY``, with ``LIMIT`` and ``OFFSET``:

.. code:: python

  # The top 10 largest countries in the world by population
  query = sql[
      (c.name for c in db.country)
      .order_by(c.population.desc())
      .limit(10)
  ]

  print(query)
  # SELECT country_1.name
  # FROM country AS country_1
  # ORDER BY country_1.population DESC
  # LIMIT ? OFFSET ?

  res = engine.execute(query).fetchall()
  for line in res:
      print(line)
  # (u'China',)
  # (u'India',)
  # (u'United States',)
  # (u'Indonesia',)
  # (u'Brazil',)
  # (u'Pakistan',)
  # (u'Russian Federation',)
  # (u'Bangladesh',)
  # (u'Japan',)
  # (u'Nigeria',)


In general, apart from the translation of generator expressions (and
their guards) into ``SELECT`` an ``WHERE`` clauses, the rest of the
functionality of SQL (like the ``.order_by()``, ``.limit()``,
etc. functions shown above) is accessed as in the `SQLAlchemy
Expression Language`__. See the `unit tests`__ for a fuller set of
examples of what PINQ can do, or browse the SQLAlchemy docs mentioned
earlier.

__ http://docs.sqlalchemy.org/en/latest/core/tutorial.html#ordering-grouping-limiting-offset-ing
__ https://github.com/lihaoyi/macropy/blob/master/macropy/experimental/test/pinq.py

PINQ demonstrates how easy it is to use macros to lift python snippets
into an AST and cross-compile it into another language, and how nice
the syntax and semantics can be for these embedded DSLs. PINQ's entire
implementation comprises about `100 lines of code`__, which really
isn't much considering how much it does for you!

__ https://github.com/lihaoyi/macropy/blob/master/macropy/experimental/pinq.py
