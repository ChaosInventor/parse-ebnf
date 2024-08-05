.. _tree:
.. index:: parse tree

Parse tree
==========

The parse-ebnf parse tree is represented using the |PT| class:

.. autoclass:: parse_ebnf.PT

Each node in the parse tree inherits from the |Node| class:

.. autoclass:: parse_ebnf.nodes.Node

.. index:: abstract nodes

The |Node| class along with a few other node classes do not appear
in the tree; they act as abstract base classes:

.. autoclass:: parse_ebnf.nodes.Leaf
.. autoclass:: parse_ebnf.nodes.Primary

Parse trees and all nodes implement the ``repr`` and ``str`` functions. Taking
``repr()`` of a node or parse tree gives a debug string that describes the
structure of a parse tree or node. Taking ``str()`` of a node or parse tree
gives the yield of said node or parse tree.

``str()`` applied to a parse tree is equivalent to applying it to its root. On
the other hand, ``repr()`` is not equivalent between a parse tree and its root,
the parse tree adds an extra line.

.. _partial:
.. index:: partial trees

Partial trees
-------------

If an error occurs during parsing, a partial tree is created. A partial tree is
valid for the most part, with the exception of partial nodes. Partial nodes have
valid parent and child links, however their coordinates, child specification
and data are not guaranteed to be valid. This means that a partial parse tree as
a whole is valid up to the point of failure, anything beyond that is undefined.

Partial trees and nodes operate under the following rules:

- A partial tree has a partial root;
- A partial node has a partial last child, all other children are valid;

See the :ref:`example <example>` for how to get and handle partial trees.

.. index:: parsing nodes

Node types
----------

This section contains a reference of all node types found in the |PT|.

Each node type contains:

- A short description of what it represents;
- A list of possible parent nodes;
- A child node list specification.

The parent list and child node specification are taken directly from the tests.
The child nodes specification uses functions whose meaning is described in the
:ref:`notation section <childrenNotation>`.

The nodes are ordered in roughly the same way as they appear in the parse tree,
going from the root to the leafs.

.. _childrenNotation:
.. index:: child specification

Notation
++++++++

.. _childrenEntry:

The types, order and count of child nodes for each node type is documented using
a list of node types and functions called ``children``. These functions enclose
a node type and modify how many times, if it at all it appears. Some functions
set what data a |Leaf| node may hold.

Child nodes appear in the same order as in the child node specification. For
example say the node ``A`` had a child spec of:

.. code-block:: py

   children = [ Identifier, Space, Identifier ]

That means that any instance of ``A`` is guaranteed to have a child list of
length 3 that first contains an |Identifier| as the first element, followed by
a |Space| and finally another |Identifier| instance as the last element.

:ref:`A number of functions <childFuncReference>` modify the number of times a
child node appears. For example the child specification of |Product|:

.. code-block:: py

    children = [ Identifier, maybe(Space), literal("="), maybe(Space), DefinitionList, maybe(Space), literal([";", "."]) ]

Means that any one |Product| instance may have between 4 and 7 child nodes. Of
those, the first is always an |Identifier|. A single |Space| instance might
follow, or it might not. Then a |Literal| with the data ``=`` always follows,
with an optional |Space|. A single |DefinitionList| comes after and another
optional |Space| follows. The last node is guaranteed to be a |Literal| that has
its data set either to ``.`` or ``;``.

As another example, the child spec of |Comment|:

.. code-block:: py

    children = [ literal("(*"), zero_or_more(either(Comment, Text)), literal("*)") ]

All comments start with a |Literal| with the data ``(*``, followed by any
number, including zero, or either |Comment| or |Text| instances. Finally the
last node is always a |Literal| with the data ``*)``. The length of the children
list can be anywhere from 2 to any finite number.

As a final example, an empty child specification:

.. code-block:: py

   children = [ ]

This means that the node has no children, a unique characteristic of |Leaf|
nodes.

.. _parentEntry:

The ``parents`` list gives the possible nodes types that may be a parent of a
node. For example:

.. code-block:: py

   parents = [ Root, Product, Comment ]

Means that the node's parent may either be a |Root| instance, a |Product|
instance or a |Comment| instance.

.. _childFuncReference:
.. index:: child specification function reference

Function reference
******************

.. autofunction:: tests.tree_structure.literal
.. autofunction:: tests.tree_structure.either
.. autofunction:: tests.tree_structure.zero_or_more
.. autofunction:: tests.tree_structure.maybe

.. _concreteNodes:
.. index:: conrete node reference

Node reference
++++++++++++++

The |PT| always begins with the |Root| node:

.. autoclass:: parse_ebnf.nodes.Root
.. autoclass:: parse_ebnf.nodes.Comment
.. autoclass:: parse_ebnf.nodes.Product
.. autoclass:: parse_ebnf.nodes.DefinitionList
.. autoclass:: parse_ebnf.nodes.Definition
.. autoclass:: parse_ebnf.nodes.Term
.. autoclass:: parse_ebnf.nodes.Exception
.. autoclass:: parse_ebnf.nodes.Repetition
.. autoclass:: parse_ebnf.nodes.Terminal
.. autoclass:: parse_ebnf.nodes.Repeat
.. autoclass:: parse_ebnf.nodes.Option
.. autoclass:: parse_ebnf.nodes.Group
.. autoclass:: parse_ebnf.nodes.Special
.. autoclass:: parse_ebnf.nodes.Identifier
.. autoclass:: parse_ebnf.nodes.EmptyString
.. autoclass:: parse_ebnf.nodes.Text
.. autoclass:: parse_ebnf.nodes.Space
.. autoclass:: parse_ebnf.nodes.Literal
.. autoclass:: parse_ebnf.nodes.Number

