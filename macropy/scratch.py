from macropy.macros.adt import macros, case
from macropy.macros.tracing import macros, show_expanded, trace

with show_expanded:
    @case
    class Point(x, y):
        pass
