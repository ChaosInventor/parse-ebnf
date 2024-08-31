# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

from typing import Callable


class PT:
    """A parse tree for EBNF.

    Contains the following variables:

    - ``root``, the root node of the tree, an instance of |Root|;
    - ``count``, the number of nodes in the tree;
    - ``height``, the height of the tree;
    - ``maxDegree``, the maximum number of children that a single node has in
      the tree.

    And the following functions:

    - ``unparse``, pass a write function(a function that works just like the
      write function for files) to write the text that the parse tree was
      created from.
    - ``write``, use with a write function to dump a textual representation of
      the parse tree, mainly meant for debugging.

    For parsing check the :doc:`parsing <parsing>` section.
    """
    root = None
    count = 0
    height = 0
    maxDegree = 0

    def unparse(self, write):
        """Write the text this tree was generate to using ``write``.

        ``write`` is a function that works exactly like write for files - it
        takes in a string and write it to the output. Note that the return value
        is ignored.
        """
        write(str(self.root))
    def write(self, write):
        """Same as `unparse` except that a textual representation meant for
        debugging is written.
        """
        write(repr(self))

    def __init__(self):
        self.root = None
        self.count = 0
        self.height = 0
        self.maxDegree = 0
    def __str__(self):
        """Returns the text that this tree was generated from."""
        return str(self.root)
    def __repr__(self):
        """Returns a textual representation of this tree meant for debugging."""
        return f'PT{{count = {self.count}, height = {self.height}, maxDegree={self.maxDegree}}}:\n{self.root!r}'

class EBNFError(Exception):
    """Base class of all parse_ebnf errors. Does not define anything."""
