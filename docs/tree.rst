.. _tree:

Tree structure
==============

This is a list of all tree node types, roughly ordered as they appear in the
tree from top to bottom.

Notation
--------

To simplify writing out which node types go where in the tree, we'll use the
following notation:

.. index:: parent entry

.. _parentEntry:

Each node will have an entry on which node type its parent has, labeled
``Parent type``.

.. index:: children entry

.. _childrenEntry:

Each node will have an entry titled ``Children`` that will contain an expression
denoting which nodes types can be found as this node's children. These
expression will be analogous to grammars. The expression are structured as
follows:

``NODE_TYPE, (NODE_TYPE | OTHER_TYPE), NODE_TYPE?, NODE_TYPE*, NODE_TYPE+``

Read from left to right, they describe which node types can be found at which
positions. The first node would be of type of the first entry, the second node
of the type after the comma, etc.

.. index:: groups

.. _groups:

There are also groups, denoted with brackets. Multiple node types may be written
inside them, all seprate using a bar, ``|``. It it to be interpreted as the
node type being either of the list types. The actual type must be disambiguated
using ``isinstance``.

Finally we have 3 suffixes:

.. index:: suffixes

.. _optional:

- ? -- the node type or group may be omitted;

.. _any:

- \* -- the node type or group may be omitted or occur an unbounded finite
  number of times in the list;

.. _more:

- \+ -- the node type or group occurs at least once, but may occur an additional
  unbounded finite amount of time in the list.

|Literal|\ s also get another suffix:

``= 'string' | 'other string'``

Which means that the text data that the literal holds may be one of the
presented possibilities.

See the below documentation for examples.

Tree classes
------------

The |AST| always begins with the ``root`` node:

.. autoclass:: parse_ebnf.Root
.. autoclass:: parse_ebnf.Text
.. autoclass:: parse_ebnf.Comment
.. autoclass:: parse_ebnf.Space
.. autoclass:: parse_ebnf.Product
.. autoclass:: parse_ebnf.Identifier
.. autoclass:: parse_ebnf.Literal
.. autoclass:: parse_ebnf.DefinitionList
.. autoclass:: parse_ebnf.Definition
.. autoclass:: parse_ebnf.Term
.. autoclass:: parse_ebnf.Repetition
.. autoclass:: parse_ebnf.Terminal
.. autoclass:: parse_ebnf.Repeat
.. autoclass:: parse_ebnf.Option
.. autoclass:: parse_ebnf.Special
.. autoclass:: parse_ebnf.Group
.. autoclass:: parse_ebnf.Empty
.. autoclass:: parse_ebnf.Exception
.. autoclass:: parse_ebnf.EmptyTerm

