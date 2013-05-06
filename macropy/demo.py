from macropy.macros.string_interp import macros, s
from macropy.macros2.linq import macros, sql
from macropy.macros.quicklambda import macros, f
from macropy.macros2.tracing import macros, trace
from macropy.macros2.tracing import *
from macropy.macros2.peg import macros
from macropy.macros2.peg import *
from macropy.macros.adt import macros
import math
def foo():
    with trace:
        sum([x + 5 for x in range(3)])


foo()