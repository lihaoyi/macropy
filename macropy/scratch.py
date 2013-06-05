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
for line in results: print line