Testing
=======

Running ``pytest`` in the repository's root will cause all tests to be run.

Tests cover the parser and examples given in documentation. See
``tests/test_parser.py`` for the most important tests.

Resources directory
--------------------

The ``tests/resouces/`` directory contains two subdirectories:

- ``tests/resources/valid/``
- ``tests/resources/invalid/``

The ``valid/`` subdirectory contains example files that are meant to be parsed
without any errors.

The ``invalid/`` subdirectory contains example files that have one or more
errors in them.

These resources are used by all tests as input data.

Tree structure
--------------

The documented tree structure and tested tree structure are kept in sync via the
``tests/tree_structure`` directory. Under this directory each instantiated node
type has its own file describing its possible parent and children node types
along with their order and count.

Each file under ``tests/tree_structure`` is named after the node is describes
with an added ``.py`` suffix. For example, the |Comment| node's structure is
described in ``tests/tree_structure/Comment.py``.

On the fourth line of each file, the variable ``parents`` is defined, holding a
list of possible parent types.

On the fifth line of each file, the variable ``children`` is defined, holding
a list of children in the order they appear in the tree. Functions defined in
``tests/tree_structure/__init__.py`` are used to :ref:`specify their number and
contents <childrenNotation>`.
