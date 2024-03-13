Classes
=======

To use this package, you'll only really need two classes:

- |PT|
- |Node|

Use |PT| to parse your input, and |Node| and it's
:doc:`derived classes <tree>` to traverse the tree.

.. autoclass:: parse_ebnf.PT
   :members: parse, unparse, write

.. autoclass:: parse_ebnf.nodes.Node

