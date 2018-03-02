.. _enums:

Enums
-----

.. code:: python

  from macropy.case_classes import macros, enum

  @enum
  class Direction:
      North, South, East, West

  print(Direction(name="North")) # Direction.North

  print(Direction.South.name)    # South

  print(Direction(id=2))         # Direction.East

  print(Direction.West.id)       # 3

  print(Direction.North.next)    # Direction.South
  print(Direction.West.prev)     # Direction.East

  print(Direction.all)
  # [Direction.North, Direction.East, Direction.South, Direction.West]


MacroPy also provides an implementation of `Enumerations`__ , heavily
inspired by the `Java implementation`__ and built upon `Case Classes
<case_classes>`:ref:. These are effectively case classes with:

__ http://en.wikipedia.org/wiki/Enumerated_type
__ http://docs.oracle.com/javase/tutorial/java/javaOO/enum.html

- A fixed set of instances;
- Auto-generated ``name``,  ``id``, ``next`` and ``prev`` fields;
- Auto-generated ``all``  list, which enumerates all instances;

- A ``__new__`` method that retrieves an existing instance, rather than
  creating new ones

Note that instances of an Enum cannot be created manually: calls such
as ``Direction(name="North")`` or ``Direction(id=2)`` attempt to retrieve
an existing Enum with that property, throwing an exception if there is
none. This means that reference equality is always used to compare
instances of Enums for equality, allowing for much faster equality
checks than if you had used `Case Classes <case_classes>`:ref:.

Definition of Instances
~~~~~~~~~~~~~~~~~~~~~~~

The instances of an Enum can be declared on a single line, as in the
example above, or they can be declared on subsequent lines:

.. code:: python

  @enum
  class Direction:
      North
      South
      East
      West


or in a mix of the two styles:

.. code:: python

  @enum
  class Direction:
      North, South
      East, West


The basic rule here is that the body of an Enum can only contain bare
names, function calls (show below), tuples of these, or function defs:
no other statements are allowed. In turn the bare names and function
calls are turned into instances of the Enum, while function defs
(shown later) are turned into their methods. This also means that
unlike `Case Classes <case_classes>`:ref:, Enums cannot have a `body
initializer <body_initializer>`:ref:.

Complex Enums
~~~~~~~~~~~~~

.. code:: python

  @enum
  class Direction(alignment, continents):
      North("Vertical", ["Northrend"])
      East("Horizontal", ["Azeroth", "Khaz Modan", "Lordaeron"])
      South("Vertical", ["Pandaria"])
      West("Horizontal", ["Kalimdor"])

      @property
      def opposite(self):
          return Direction(id=(self.id + 2) % 4)

      def padded_name(self, n):
          return ("<" * n) + self.name + (">" * n)

  # members
  print(Direction.North.alignment) # Vertical
  print(Direction.East.continent)  # ["Azeroth", "Khaz Modan", "Lordaeron"]

  # properties
  print(Direction.North.opposite)  # Direction.South

  # methods
  print(Direction.South.padded_name(2)) # <<South>>

Enums are not limited to the auto-generated members shown above. Apart
from the fact that Enums have no constructor, and no body initializer,
they can contain fields, methods and properties just like :ref:`Case
Classes <case_classes>` do. This allows you to associate arbitrary
data with each instance of the Enum, and have them perform as
full-fledged objects rather than fancy integers.
