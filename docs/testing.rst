Testing
=======

In order to test this package, simply run ``pytest`` in the ``tests/`` directory.

The tests will make sure that the generated parse tree's yield is the same as
the input, which is a collection of files in the ``tests/resources/`` directory.

The tests will also check that the start/end line/column coordinates are valid
in respect to the node's yield and the input, as well as testing that the parser
detects syntax errors and raises the proper exceptions.

Resources directory
--------------------

The ``tests/resouces/`` directory contains two subdirectories:

- ``tests/resources/valid/``
- ``tests/resources/invalid/``

The ``valid/`` subdirectory contains example files that are meant to be parsed
without any errors.

The ``invalid/`` subdirectory contains example files that have one or more
errors in them.

