Classes
=======

To use this package, you'll only really need two classes:

- |AST|
- |ASTNode|

Use |AST| to parse your input, and |ASTNode| and it's
:ref:`derived classes <todo>` to traverse the tree.

.. autoclass:: parse_ebnf.AST
   :members: parse, unparse, write

.. autoclass:: parse_ebnf.ASTNode

