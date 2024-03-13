# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

from parse_ebnf import nodes

class ParserState:
    """A helper class for parsing, not meant to be used externally.

    Keeps track of the current line and column, `line` and `column`
    respectively, as well as the currently read string, `c`. It also has a
    reference to the AST it belongs, `ast`, and to the read function `readFunc`

    Has lists containing constant characters that are used as terminals those
    being:

     - `DEFINITION_SEPARATORS`
     - `PRODUCT_TERMINATOR_SYMBOLS`
     - `TERMINAL_START_SYMBOLS`
     - `TERM_START_SYMBOLS`
     - `BRACKET_START_SYMBOLS`
     - `BRACKET_END_SYMBOLS`

    Finally has two helper functions for reading input:

     - `read`
     - `readNoEOF`

    They help by maintaining `line`, `column` and `c`.
    """
    ast = None
    readFunc = None
    c = ''
    line = 0
    column = 0

    DEFINITION_SEPARATORS = ['|', '/', '!']
    PRODUCT_TERMINATOR_SYMBOLS = [';', '.']
    TERMINAL_START_SYMBOLS = ['"', "'", "`"]
    TERM_START_SYMBOLS = ['(', '[', '{', '?'] + TERMINAL_START_SYMBOLS
    BRACKET_START_SYMBOLS = ['(', '(/', '(:']
    BRACKET_END_SYMBOLS = [')', '/)', ':)']

    def read(self, n):
        """Reads `n` characters, updates `line`, `column` and `c`, returns self.c"""
        self.c = self.readFunc(n)
        for c in self.c:
            if c == '\n':
                self.line += 1
                self.column = 0
            else:
                self.column += 1

        return self.c
    def readNoEOF(self, n, msg="Unexpected EOF"):
        """Just like `read` except that it raises a `SyntaxError` with `msg` if
        no characters were read, that is EOF has been reached.
        """
        self.read(n)

        if len(self.c) == 0:
            raise SyntaxError(msg)

        return self.c

    def __init__(self, read, ast):
        """ Create a new parser state for the AST `ast` with the read function
        `read`.
        """
        assert isinstance(ast, AST), "Expected an AST obejct"
        assert read != None, "Expected a read function"
        self.ast = ast
        self.readFunc = read
        self.line = 1
        self. column = 0
        self.read(1)

class AST:
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

        from parse_ebnf import AST
        from io import StringIO

        ast1 = AST()
        ast2 = AST()

        file = open('your-ebnf-file.ebnf', 'r')

        ast1.parse(file.read);
        with StringIO('rule = term | another term;') as f:
            ast2.parse(f.read)

        #You now have two useable parse trees, ast1 and ast2

        #Print the text that the first child of the root was created from, the
        #first child will probably be an CommentNode or ASTRule.
        print(repr(ast1.root.children[0]))

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

    def parse(self, read):
        """Parse an input from ``read``.

        ``read`` is a function that works exactly like read for files - it takes
        in a positive number or zero, and returns a string of that size or less
        if EOF is near.
        """
        self.root.parse(ParserState(read, self))
    def unparse(self, write):
        """Write the text this tree was generate to using ``write``.

        ``write`` is a function that works exactly like write for files - it
        takes in a string and write it to the output. Note that the return value
        in this case is ignored.
        """
        write(repr(self.root))
    def write(self, write):
        """Same as `unparse` except that a textual representation meant for
        debugging is written.
        """
        write(str(self))

    def __init__(self):
        self.root = nodes.Root()
        print(nodes)
        self.count = 1
        self.height = 0
        self.maxDegree = 0
    def __repr__(self):
        """Returns the text that this tree was generated from."""
        return repr(self.root)
    def __str__(self):
        """Returns a textual representation of this tree meant for debugging."""
        return f'AST{{count = {self.count}, height = {self.height}, maxDegree={self.maxDegree}}}:\n{str(self.root)}'

