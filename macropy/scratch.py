from macropy.macros.pattern import macros, patterns
from macropy.macros.adt import macros, case

@case
class Rect(p1, p2):
    pass

@case
class Line(p1, p2): pass


@case
class Point(x, y):
    pass

def area(rect):
    with patterns:
        Rect(Point(x1, y1), Point(x2, y2)) << rect
        return (x2 - x1) * (y2 - y1)

print area(Line(Point(1, 1), Point(3, 3))) # 4
# macropy.macros.pattern.PatternMatchException: Matchee should be of type <class 'scratch.Rect'>