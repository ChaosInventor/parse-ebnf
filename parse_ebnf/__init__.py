# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

from parse_ebnf import nodes
from io import StringIO
from collections.abc import Callable

class PT:
    """A parse tree for EBNF.

    Contains the following variables:

    - ``root``, the root node of the tree, an instance of :py:class:`Root`;
    - ``count``, the number of nodes in the tree;
    - ``height``, the height of the tree;
    - ``maxDegree``, the maximum number of children that a single node has in
      the tree.

    And the following functions:

    - ``parse``, use with a read function(a function that works just like the
      read function for files) to parse an input.
    - ``unparse``, use with a write function(a function that works just like the
      write function for files) to write the text that the parse tree was
      created from.
    - ``write``, use with a write function to dump a textual representation of
      the parse tree, mainly meant for debugging.

    Example:

    .. code-block:: python

        from parse_ebnf import PT, parsing
        from io import StringIO

        pt1 = PT()
        pt2 = PT()

        file = open('your-ebnf-file.ebnf', 'r')

        pt1 = parsing.parse_pt(file.read)
        with StringIO('rule = term | another term;') as f:
            pt2 = parsing.parse_pt(f.read)

        #You now have two useable parse trees, pt1 and pt2

        #Print the text that the first child of the root was created from, the
        #first child will probably be an CommentNode or PTRule.
        print(repr(pt1.root.children[0]))

        #The height and maxDegree can be used to calculate the worst case size
        #for:
        #
        # - A stack, the worst case size would be the height;
        # - A queue, the worst case size would be `maxDegree ** height`.

        file.close()
    """
    root = None
    count = 0
    height = 0
    maxDegree = 0

    def unparse(self, write):
        """Write the text this tree was generate to using ``write``.

        ``write`` is a function that works exactly like write for files - it
        takes in a string and write it to the output. Note that the return value
        in this case is ignored.
        """
        write(str(self.root))
    def write(self, write):
        """Same as `unparse` except that a textual representation meant for
        debugging is written.
        """
        write(str(self))

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
        return f'PT{{count = {self.count}, height = {self.height}, maxDegree={self.maxDegree}}}:\n{repr(self.root)}'

class EBNFError(Exception):
    pass

def parseFile(ebnf: str) -> PT:
    return parsing.parse_pt(open(ebnf).read)
def parseString(ebnf: str) -> PT:
    return parsing.parse_pt(StringIO(ebnf).read)
def parseFromFunction(read: Callable[[int], str]) -> PT:
    return parsing.parse_pt(read)
