# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

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

    - ``root``, the root node of the tree, an instance of :py:class:`ASTRootNode`;
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
        #first child will probably be an ASTCommentNode or ASTRuleNode.
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
        self.root = ASTRootNode()
        self.count = 1
        self.height = 0
        self.maxDegree = 0
    def __repr__(self):
        """Returns the text that this tree was generated from."""
        return repr(self.root)
    def __str__(self):
        """Returns a textual representation of this tree meant for debugging."""
        return f'AST{{count = {self.count}, height = {self.height}, maxDegree={self.maxDegree}}}:\n{str(self.root)}'


class ASTNode:
    """Base class of all AST nodes.

    AST nodes differ only in what nodes are their ``parent`` and which nodes
    are their ``children``, more info at the :doc:`tree structure <tree>`.
    This node type in particular is not used in the |AST|, it only serves as a
    base class for all other node types. Using ``isinstance`` you can resolve
    a node's type.

    Contains the following variables:

    - ``parent`` -- the parent node of this node. It is ``None`` only for
      |ASTRootNode|.
    - ``children`` -- a list of this node's children. Empty only for instance of
      |ASTTextNode|.
    - ``depth`` -- an integer denoting how deep a node is in the tree. The root
      is defined as being at depth 0, it's children at depth 1, etc.
    - ``startLine`` -- the line where the text that this node is comprised of
      starts, inclusively. Counting starts from 1, and is incremented each time
      a newline is encountered in the input;
    - ``startColumn`` -- the column where the text that this node is comprised
      of starts, inclusively. Counting starts at 1, and in incremented every
      character. Each newline resets the counter to 0;
    - ``endLine`` -- like ``startLine`` except that this is where the text ends,
      exclusively;
    - ``endColumn`` -- like ``startColumn`` except that this is where the text
      ends, exclusively.

    The following always holds for coordinates:

    - `startLine` >= 0
    - `endLine` >= 0
    - `startColumn` >= 0
    - `startLine` <= `endLine`
    - if `startColumn` > `endColumn`: repr(node) == '' else `endColumn` >= 0

    .. note :: The end coordinates also take into account child nodes. The
       children's text is also counted as the parent's text.
    """
    parent = None
    children = []
    startLine = 0
    startColumn = 0
    endLine = 0
    endColumn = 0
    depth = 0

    def unparse(self, write):
        write(repr(self))

    def addChild(self, node, ast):
        self.children.append(node)
        node.parent = self
        node.depth = self.depth + 1

        ast.count += 1
        ast.height = node.depth if node.depth > ast.height else ast.height
        ast.maxDegree = len(self.children) if len(self.children) > ast.maxDegree else ast.maxDegree

        return node
    def write(self, write, depth=0):
        write(str(self))
        if len(self.children) > 0:
            write(':\n')
            for child in self:
                for _ in range(depth):
                    write('\t')
                child.write(write, depth+1)
        else:
            write('\n')

    def __init__(self, startLine=0, startColumn=0, endLine=0, endColumn=0):
        self.parent = None
        self.children = []
        self.startLine = startLine
        self.startColumn = startColumn
        self.endLine = endLine
        self.endColumn = endColumn
        self.depth = 0

    def __iter__(self):
        return self.children.__iter__()
    def __str__(self):
        ret = f"{self.startLine},{self.startColumn}-{self.endLine},{self.endColumn}\n"
        if len(self.children) > 0:
            for child in self:
                for i in range(child.depth):
                    ret += '\t'
                ret += str(child)
        return ret
    def __repr__(self):
        ret = ''
        for child in self:
            ret += repr(child)
        return ret

    def _parseNode(self, parser, node):
        self.addChild(node, parser.ast)
        return node.parse(parser)

class ASTRootNode(ASTNode):
    """ The root AST node.

    .. rubric:: :ref:`Parent type <parentEntry>`

    ``None``

    .. rubric:: :ref:`Children <childrenEntry>`

    (|ASTProductNode| |or| |ASTCommentNode| |or| |ASTSpaceNode|)\ |any|

    """
    def parse(self, parser):
        self.startLine = 1
        self.startColumn = 1

        while len(parser.c) > 0:
            if parser.c == '(':
                self._parseNode(parser, ASTCommentNode())
                parser.read(1)
            elif parser.c.isalpha():
                self._parseNode(parser, ASTProductNode())
            elif parser.c.isspace():
                self._parseNode(parser, ASTSpaceNode())
            else:
                raise SyntaxError(f"Unexpected character, {parser.c}, at file level at {parser.line},{parser.column}")

        self.endLine = parser.line
        self.endColumn = parser.column
        return self

    def __str__(self):
        return f"Root:{super().__str__()}"

class ASTTextNode(ASTNode):
    """ Base class for leaf nodes.

    This node is a base class for all leaf nodes, nodes whose ``children`` list
    is empty.

    .. note:: Only leafs nodes contain text data in the tree.

    This node has the following variables:

    - Variables inherited from |ASTNode|;
    - ``data`` -- the text content of the node, a string.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTTerminalNode| |or| |ASTSpaceNode|.

    .. rubric:: :ref:`Children <childrenEntry>`

    ``None`` -- These nodes and their derived classes are always leaf nodes.

    """
    data = ''

    def parse(self, parser):
        self.startLine = parser.line
        self.startColumn = parser.column

        while parser.c != self.start:
            self.data += parser.c
            parser.readNoEOF(1, f"EOF before termination of text started at {self.startLine},{self.startColumn}")

        self.endLine = parser.line
        self.endColumn = parser.column - 1
        return self

    def __init__(self, start=None, data=''):
        super().__init__()
        self.data = data
        self.start = start
    def __repr__(self):
        return self.data
    def __str__(self):
        return f"Text({self.data}):{super().__str__()}"
class ASTCommentNode(ASTTextNode):
    """Nodes holding EBNF comments.

    Comments in EBNF are enclosed by ``(*``, ``*)`` pairs. Nesting is allowed.

    The ``data`` string does **NOT** contain the enclosing comment markers.
    Nested comment markers are included however. ``repr`` returns a proper
    comment string.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTRootNode|

    .. rubric:: :ref:`Children <childrenEntry>`

    ``[]``, leaf node, see |ASTTextNode|.

    """
    def parse(self, parser):
        assert parser.c == '(', f"Expected current character to be '(', not {parser.c}."

        self.startLine = parser.line
        self.startColumn = parser.column

        parser.read(1)
        if parser.c != '*':
            raise SyntaxError(f"Expected '*' at {parser.line},{parser.column} since previous was a '('")

        parser.read(1)
        #Keeps track of comment recursion
        depth = 0
        #Loop is broken when '*)' is encountered and depth is 0
        while True:
            if parser.c == '*':
                oc = parser.c
                parser.read(1)

                if parser.c == ')':
                    if depth <= 0:
                        break;
                    else:
                        depth -= 1

                self.data += oc
            elif parser.c == '(':
                self.data += parser.c
                parser.read(1)
                if parser.c == '*':
                    depth += 1

            self.data += parser.c
            parser.readNoEOF(1, "Commend not terminated before EOF")

        self.endLine = parser.line
        self.endColumn = parser.column

        return self

    def __repr__(self):
        return f"(*{self.data}*)"
    def __str__(self):
        return f"Comment({self.data}):{ASTNode.__str__(self)}"
class ASTSpaceNode(ASTTextNode):
    """Node holding whitespace.

    .. rubric:: :ref:`Parent type <parentEntry>`

    ``Any``, just about every node that is not a leaf node holds this node.

    .. rubric:: :ref:`Children <childrenEntry>`

    ``None``, it is a leaf node, see |ASTTextNode|.
    """
    def parse(self, parser):
        assert parser.c.isspace(), f"Expected the current character to be a space, not {parser.c}"
        self.startLine = parser.line
        self.startColumn = parser.column

        self.data += parser.c
        self.endLine = parser.line
        self.endColumn = parser.column
        while parser.read(1).isspace():
            self.data += parser.c
            self.endLine = parser.line
            self.endColumn = parser.column

        return self

    def __init__(self, data=''):
        super().__init__(None, data)
    def  __str__(self):
        return f"Space:{ASTNode.__str__(self)}"
class ASTIdentifierNode(ASTTextNode):
    """Node holding an identifier.

    Identifiers are alphanumeric string that do not start with a number. They
    do not contain trailing or leading whitespace, however they may contain
    whitespace in the middle.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTProductNode| |or| |ASTTermNode| |or| |ASTExceptionNode|.

    .. rubric:: :ref:`Children <childrenEntry>`

    ``None``, it is a leaf node, see |ASTTextNode|.
    """
    def parse(self, parser):
        assert parser.c.isalpha(), f"Expected current character to be alphabetic, got {parser.c} instead."

        self.startLine = parser.line
        self.startColumn = parser.column

        self.data += parser.c
        self.endLine = parser.line
        self.endColumn = parser.column
        parser.read(1)
        while parser.c.isalpha() or parser.c.isnumeric() or parser.c.isspace():
            self.data += parser.c
            self.endLine = parser.line
            self.endColumn = parser.column
            parser.read(1)

        return self
    def trim(self, parser):
        ret = ''
        while len(self.data) > 0:
            if self.data[-1].isspace():
                ret += self.data[-1]
                self.data = self.data[:-1]
                if ret[-1] == '\n':
                    self.endLine -= 1
            else:
                if (line := self.data.rfind('\n')) != -1:
                    self.endColumn =  len(self.data[line + 1:])
                else:
                    self.endColumn = self.startColumn + len(self.data) - 1
                break

        if len(ret) > 0:
            space = ASTSpaceNode(ret[::-1])

            space.startLine = self.endLine
            space.startColumn = self.endColumn + 1

            space.endLine = space.startLine
            space.endColumn = 0
            onLastLine = True
            for c in ret:
                if c == '\n':
                    space.endLine += 1
                    onLastLine = False
                elif onLastLine:
                    space.endColumn += 1

            if space.startLine == space.endLine:
                space.endColumn = space.startColumn + len(ret) - 1

            return space
        else:
            return None

    def  __str__(self):
        return f"Identifier({self.data}):{ASTNode.__str__(self)}"
class ASTLiteralNode(ASTTextNode):
    """Node holding one or more characters.

    The actual character sequence depends on the parent. The parent nodes have
    documentation pertaining to the exact sequence.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTProductNode| |or| |ASTDefinitionListNode| |or| |ASTDefinitionNode| |or|
    |ASTTermNode| |or| |ASTExceptionNode| |or| |ASTRepetitionNode| |or|
    |ASTTerminalNode| |or| |ASTRepeatNode| |or| |ASTOptionNode| |or|
    |ASTGroupNode| |or| |ASTSpaceNode|.

    .. rubric:: :ref:`Children <childrenEntry>`

    ``None``, it is a leaf node, see |ASTTextNode|.
    """
    def parse(self, parser):
        self.startLine = parser.line
        self.startColumn = parser.column

        #Copy literals with index info
        literals = []
        i = 0
        for lit in self.literals:
            literals.append((lit, i))
            i += 1
        match = None
        self.endLine = parser.line
        self.endColumn = parser.column
        while True:
            lits = literals[::]
            for literal in lits:
                if parser.c != literal[0][0]:
                    literals.remove(literal)
            if len(literals) == 0:
                if match != None:
                    self.data = match
                    return self
                else:
                    break
            lits = literals[::]
            for literal in lits:
                index = literals.index(literal)
                literals[index] = (literal[0][1:], literal[1])
                if len(literals[index][0]) == 0:
                    literals.pop(index)
                    match = self.literals[literal[1]]

            self.endLine = parser.line
            self.endColumn = parser.column
            parser.read(1)

        if match != None:
            self.data = match
            return self

        raise SyntaxError(f"Could not match any literals {self.literals} starting at {self.startLine},{self.startColumn}")

    def __init__(self, literals, data=''):
        assert len(literals) > 0, "Literal cannot be empty"
        super().__init__(data)
        self.literals = literals
    def __str__(self):
        return f"Literal({self.data}):{ASTNode.__str__(self)}"

class ASTProductNode(ASTNode):
    """ A node holding a product.

    A product is a grammar rule, those of the form:

    ``something = another | third, 'a';``

    This node has the following variables:

    - Those inherited from |ASTNode|;
    - ``lhs``, the left hand side of the rule, the first |ASTIdentifierNode| of
      the children;
    - ``rhs``, the right had side of the rule, the first |ASTDefinitionListNode|
      of the children.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTRootNode|.

    .. rubric:: :ref:`Children <childrenEntry>`

    |ASTSpaceNode|\ |maybe|, |ASTIdentifierNode|, |ASTSpaceNode|\ |maybe|,
    |ASTLiteralNode| = '=', |ASTSpaceNode|\ |maybe|, |ASTDefinitionListNode|,
    |ASTSpaceNode|\ |maybe|, |ASTLiteralNode| = ';' | '.'
    """
    lhs = None
    rhs = None

    def parse(self, parser):
        assert parser.c.isalpha(), f"Expected current character to be alphabetic, got {parser.c} instead."

        self.startLine = parser.line
        self.startColumn = parser.column

        ident = self._parseNode(parser, ASTIdentifierNode())

        if (space := ident.trim(parser)) != None:
            self.addChild(space, parser.ast)

        self._parseNode(parser, ASTLiteralNode(['=']))

        if parser.c.isspace():
            self._parseNode(parser, ASTSpaceNode())

        self._parseNode(parser, ASTDefinitionListNode())

        self.endLine = parser.line
        self.endColumn = parser.column
        self._parseNode(parser, ASTLiteralNode(parser.PRODUCT_TERMINATOR_SYMBOLS))

        return self

    def __init__(self, lhs=None, rhs=None, ast=None):
        super().__init__()
        if lhs != None or rhs != None:
            assert isinstance(ast, AST), f"Expected an abstract syntax tree, not a {ast.__class__}"
        if lhs != None:
            self.lhs = lhs
            self.addChild(lhs, ast)
        if rhs != None:
            self.rhs = rhs
            self.addChild(rhs, ast)
    def __str__(self):
        return f"Product:{super().__str__()}"

class ASTDefinitionListNode(ASTNode):
    """ Node containing a list of definitions.

    Definitions are the lists of concatenations. Definitions are placed
    in-between alterations symbols. This node can be seen as holding all
    alternatives of a rule.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTProductNode| |or| |ASTRepetitionNode| |or| |ASTOptionNode| |or|
    |ASTGroupNode|.

    .. rubric:: :ref:`Children <childrenEntry>`

    |ASTSpaceNode|\ |maybe|, (|ASTDefinitionNode|, |ASTSpaceNode|\ |maybe|,
    |ASTLiteralNode| = '|' | '/' | '!')\ |any|, |ASTSpaceNode|\ |maybe|.
    """
    def parse(self, parser):
        self.startLine = parser.line
        self.startColumn = parser.column

        while True:
            if parser.c.isspace():
                self._parseNode(parser, ASTSpaceNode())

            definition = self._parseNode(parser, ASTDefinitionNode())

            if parser.c.isspace():
                self._parseNode(parser, ASTSpaceNode())

            self.endLine = parser.line
            self.endColumn = parser.column - 1
            if parser.c in parser.DEFINITION_SEPARATORS:
                lit = ASTLiteralNode(parser.DEFINITION_SEPARATORS + ['/)']).parse(parser)

                #Special case for alternate '}'
                if lit.data == '/)':
                    self.endLine = parser.line
                    self.endColumn = parser.column - 3
                    return self, lit
                else:
                    self.addChild(lit, parser.ast)
            else:
                break

        return self, None

    def __str__(self):
        return f"Definition list:{super().__str__()}"

class ASTDefinitionNode(ASTNode):
    """A node holding a definition.

    A definition is the list of concatenations on the right hand side of a rule.
    This node can be seen as having a sequence that a rule needs to match.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTDefinitionListNode|

    .. rubric:: :ref:`Children <childrenEntry>`

    |ASTSpaceNode|\ |maybe|, ((|ASTTermNode| |or| |ASTEmptyTerm|), |ASTSpaceNode|\ |maybe|,
    |ASTLiteralNode| = ',', |ASTSpaceNode|\ |maybe|)\ |any|.

    """
    def parse(self, parser):
        self.startLine = parser.line
        self.startColumn = parser.column

        term = None
        while True:
            if len(parser.c) == 0:
                raise SyntaxError(f"Unexpected EOF in definition started at {self.startLine},{self.startColumn}")
            if parser.c.isspace():
                self._parseNode(parser, ASTSpaceNode())
            elif parser.c.isalpha() or parser.c.isnumeric() or parser.c in parser.TERM_START_SYMBOLS:
                if term != None:
                    raise SyntaxError(f"Start of another term at {parser.line},{parser.column} before previous term at {term.startLine},{term.startColumn} properly terminated")
                term = self._parseNode(parser, ASTTermNode())
            elif parser.c == ',':
                if term == None:
                    self._parseNode(parser, ASTEmptyTerm())
                self._parseNode(parser, ASTLiteralNode([',']))
                term = None
            else:
                #Let the definition list handle it
                break;

        self.endLine = parser.line
        self.endColumn = parser.column - 1
        return self

    def __str__(self):
        return f"Definition:{super().__str__()}"

class ASTTermNode(ASTNode):
    """ Node holding a single term.

    Terms are values that a rule can take, they may be either:

    - Terminals;
    - Non-terminals;
    - Groups.

    This node has the following variables:

    - Those inherited from |ASTNode|;
    - ``repetition`` -- an |ASTRepetitionNode|, the one in the children list;
    - ``primary`` -- the term that this node is defined as, the one in the
      children list, may either be:

        - |ASTTerminalNode|;
        - |ASTIdentifierNode|;
        - |ASTGroupNode|;
        - |ASTRepeatNode|;
        - |ASTOptionNode|;
        - |ASTSpecialNode|.

    - ``exception`` -- an |ASTExceptionNode|, the one in the children list.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTDefinitionNode|

    .. rubric:: :ref:`Children <childrenEntry>`

    |ASTSpaceNode|\ |maybe|, |ASTRepetitionNode|\ |maybe|, |ASTSpaceNode|\
    |maybe|, (|ASTIdentifierNode| |or| |ASTTerminalNode| |or| |ASTRepeatNode|
    |or| |ASTOptionNode| |or| |ASTSpecialNode| |or| |ASTGroupNode| |or|
    |ASTEmptyNode|), (|ASTSpaceNode|\ |maybe|, |ASTLiteralNode| = '-',
    |ASTExceptionNode|)\ |maybe|.

    """
    repetition = None
    primary = None
    exception = None

    def parse(self, parser):
        self.startLine = parser.line
        self.startColumn = parser.column

        while True:
            if parser.c.isspace():
                self._parseNode(parser, ASTSpaceNode())
            elif parser.c.isalpha():
                if self.primary != None:
                    raise SyntaxError(f"Term started at {self.startLine},{self.startColumn} can only have one primary, however another defined at {parser.line},{parser.column}")
                self.primary = self._parseNode(parser, ASTIdentifierNode())
                if (space := self.primary.trim(parser)) != None:
                    self.addChild(space, parser.ast)
            elif parser.c.isnumeric():
                if self.repetition != None:
                    raise SyntaxError(f"Term can only have one repetition, another defined at {parser.line},{parser.column}, last one at {self.repetition.startLine},{self.repetition.startColumn}")
                self.repetition = self._parseNode(parser, ASTRepetitionNode())
            elif parser.c == '-':
                if self.exception != None:
                    raise SyntaxError(f"Unexpected '-', term started at {self.startLine},{self.startColumn} already has an exception defined at {self.exception.startLine},{self.exception.startColumn}")
                self._parseNode(parser, ASTLiteralNode(['-']))
                self.exception = self._parseNode(parser, ASTExceptionNode())
            elif parser.c in parser.TERMINAL_START_SYMBOLS:
                if self.primary != None:
                    raise SyntaxError(f"Term started at {self.startLine},{self.startColumn} can only have one primary, however another defined at {parser.line},{parser.column}")

                self.primary = self._parseNode(parser, ASTTerminalNode())
            elif parser.c == '{':
                if self.primary != None:
                    raise SyntaxError(f"Term started at {self.startLine},{self.startColumn} can only have one primary, however another defined at {parser.line},{parser.column}")
                self.primary = self._parseNode(parser, ASTRepeatNode())
            elif parser.c == '[':
                if self.primary != None:
                    raise SyntaxError(f"Term started at {self.startLine},{self.startColumn} can only have one primary, however another defined at {parser.line},{parser.column}")
                self.primary = self._parseNode(parser, ASTOptionNode())
            elif parser.c == '?':
                if self.primary != None:
                    raise SyntaxError(f"Term started at {self.startLine},{self.startColumn} can only have one primary, however another defined at {parser.line},{parser.column}")
                self.primary = self._parseNode(parser, ASTSpecialNode())
            elif parser.c == '(':
                if self.primary != None:
                    raise SyntaxError(f"Term started at {self.startLine},{self.startColumn} can only have one primary, however another defined at {parser.line},{parser.column}")
                lit = ASTLiteralNode(parser.BRACKET_START_SYMBOLS).parse(parser)
                if lit.data == '(':
                    self.primary = self._parseNode(parser, ASTGroupNode(lit))
                if lit.data == '(/':
                    self.primary = self._parseNode(parser, ASTRepeatNode(lit))
                if lit.data == '(:':
                    self.primary = self._parseNode(parser, ASTOptionNode(lit))
            else:
                #Let the definition handle it
                break

        if self.primary == None:
            self.primary = self._parseNode(parser, ASTEmptyNode())

        self.endLine = self.children[-1].endLine
        self.endColumn = self.children[-1].endColumn
        return self

    def __init__(self, ast=None, repetition=None, primary=None, exception=None):
        assert repetition == None or isinstance(repetition, ASTRepetitionNode), f"Repetition must be either None or an int, got {repetition}"
        assert isinstance(primary, ASTNode) or primary == None, "A term must have a primary"
        assert isinstance(exception, ASTTermNode) or exception == None, "Exception must be another term"
        if primary != None or exception != None:
            assert isinstance(ast, AST), "Expected an abstract syntax tree"

        super().__init__()
        self.repetition = repetition
        self.primary = primary
        if primary != None:
            self.addChild(primary, ast)

        self.exception = exception
        if exception != None:
            self.addChild(exception)

    def __str__(self):
        return f"Term:{super().__str__()}"

class ASTExceptionNode(ASTNode):
    """ A node holding the exception to a term.

    Exceptions are written after a term's primary, prefixed with a ``-``.
    They're terms themselves, except that they don't have exceptions and
    repetitions.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTTermNode|

    .. rubric:: :ref:`Children <childrenEntry>`

    |ASTSpaceNode|\ |maybe|, (|ASTIdentifierNode| |or| |ASTTerminalNode| |or|
    |ASTRepeatNode| |or| |ASTOptionNode| |or| |ASTSpecialNode| |or|
    |ASTGroupNode| |or| |ASTEmptyNode|).

    """
    primary = None

    def parse(self, parser):
        self.startLine = parser.line
        self.startColumn = parser.column

        while True:
            if parser.c.isspace():
                self._parseNode(parser, ASTSpaceNode())
            elif parser.c.isalpha():
                if self.primary != None:
                    raise SyntaxError(f"Term started at {self.startLine},{self.startColumn} can only have one primary, however another defined at {parser.line},{parser.column}")
                self.primary = self._parseNode(parser, ASTIdentifierNode())
                if (space := self.primary.trim(parser)) != None:
                    self.addChild(space, parser.ast)
            elif parser.c in parser.TERMINAL_START_SYMBOLS:
                if self.primary != None:
                    raise SyntaxError(f"Term started at {self.startLine},{self.startColumn} can only have one primary, however another defined at {parser.line},{parser.column}")

                self.primary = self._parseNode(parser, ASTTerminalNode())
            elif parser.c == '{':
                if self.primary != None:
                    raise SyntaxError(f"Term started at {self.startLine},{self.startColumn} can only have one primary, however another defined at {parser.line},{parser.column}")
                self.primary = self._parseNode(parser, ASTRepeatNode())
            elif parser.c == '[':
                if self.primary != None:
                    raise SyntaxError(f"Term started at {self.startLine},{self.startColumn} can only have one primary, however another defined at {parser.line},{parser.column}")
                self.primary = self._parseNode(parser, ASTOptionNode())
            elif parser.c == '?':
                if self.primary != None:
                    raise SyntaxError(f"Term started at {self.startLine},{self.startColumn} can only have one primary, however another defined at {parser.line},{parser.column}")
                self.primary = self._parseNode(parser, ASTSpecialNode())
            elif parser.c == '(':
                if self.primary != None:
                    raise SyntaxError(f"Term started at {self.startLine},{self.startColumn} can only have one primary, however another defined at {parser.line},{parser.column}")
                lit = ASTLiteralNode(parser.BRACKET_START_SYMBOLS).parse(parser)
                if lit.data == '(':
                    self.primary = self._parseNode(parser, ASTGroupNode(lit))
                if lit.data == '(/':
                    self.primary = self._parseNode(parser, ASTRepeatNode(lit))
                if lit.data == '(:':
                    self.primary = self._parseNode(parser, ASTOptionNode(lit))
            else:
                #Let the definition handle it
                break

        if self.primary == None:
            self.primary = self._parseNode(parser, ASTEmptyNode())

        self.endLine = self.children[-1].endLine
        self.endColumn = self.children[-1].endColumn
        return self

    def __init__(self, ast=None, primary=None):
        assert isinstance(primary, ASTNode) or primary == None, "A term must have a primary"
        if primary != None:
            assert isinstance(ast, AST), "Expected an abstract syntax tree"

        super().__init__()
        self.primary = primary
        if primary != None:
            self.addChild(primary, ast)

    def __str__(self):
        return f"Exception:{super().__str__()}"

class ASTRepetitionNode(ASTNode):
    """A node holding how many times at most a term may be repeated.

    This node has the following variables:

    - Those inherited from |ASTNode|;
    - ``count`` -- an integer denoting the repetition count.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTTermNode|

    .. rubric:: :ref:`Children <childrenEntry>`

    |ASTSpaceNode|\ |maybe|, |ASTLiteralNode| = '*', |ASTSpaceNode|\ |maybe|.
    """
    count = 0

    def parse(self, parser):
        assert parser.c.isnumeric(), f"Expected the current character to be a number, not {parser.c}"

        self.startLine = parser.line
        self.startColumn = parser.column

        num = parser.c
        while parser.readNoEOF(1, "EOF before proper termination of integer").isnumeric():
            num += parser.c
        self.count = int(num)

        if parser.c.isspace():
            self._parseNode(parser, ASTSpaceNode())

        self.endLine = parser.line
        self.endColumn = parser.column
        self._parseNode(parser, ASTLiteralNode(['*']))

        return self

    def __init__(self, count=0):
        super().__init__()
        self.count = count
    def __str__(self):
        return f"Repetition({self.count}):{super().__str__()}"
    def __repr__(self):
        return str(self.count) + super().__repr__()

class ASTTerminalNode(ASTNode):
    """A node holding a terminal.

    Terminals are sequences of characters that are enclosed by either:

    - ``'``;
    - ``"``;
    - ``\```.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTTermNode| |or| |ASTExceptionNode|.

    .. rubric:: :ref:`Children <childrenEntry>`

    |ASTLiteralNode| = '"' | "'" | '`', |ASTTextNode|, |ASTLiteralNode| = '"' |
    "'" | '`'.
    """
    def parse(self, parser):
        assert parser.c in parser.TERMINAL_START_SYMBOLS, f"Expected current character to be one of {parser.TERMINAL_START_SYMBOLS}, not {parser.c}"

        self.startLine = parser.line
        self.startColumn = parser.column

        lit = self._parseNode(parser, ASTLiteralNode([parser.c]))
        self._parseNode(parser, ASTTextNode(lit.data))

        self.endLine = parser.line
        self.endColumn = parser.column

        self._parseNode(parser, ASTLiteralNode([lit.data]))

        return self

    def __str__(self):
        return f"Terminal:{super().__str__()}"

class ASTRepeatNode(ASTNode):
    """ A node holding a repeatable group.

    A group enclosed by either:

    - ``{`` or ``(/``;
    - ``}`` or ``/)``.

    May be repeated any number of times, including none.

    This node has the following variables:

    - Those inherited from |ASTNode|;
    - ``lit`` -- the first literal node in the children list.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTTermNode| |or| |ASTExceptionNode|

    .. rubric:: :ref:`Children <childrenEntry>`

    |ASTLiteralNode| = '{' | '(/', |ASTDefinitionListNode|, |ASTLiteralNode| =
    '}' | '/)'.
    """
    lit = None

    def parse(self, parser):
        self.startLine = parser.line
        self.startColumn = parser.column

        if self.lit == None:
            self._parseNode(parser, ASTLiteralNode(['{']))
        else:
            self.addChild(self.lit, parser.ast)
            self.startLine = self.lit.startLine
            self.startColumn = self.lit.startColumn

        if parser.c.isspace():
            self._parseNode(parser, ASTSpaceNode())

        defList, lit = self._parseNode(parser, ASTDefinitionListNode())

        if lit != None:
            self.endLine = lit.endLine
            self.endColumn = lit.endColumn
            self.addChild(lit, parser.ast)
        else:
            self.endLine = parser.line
            self.endColumn = parser.column
            #No need to check for '/)' since the definition list would have parsed it if it were there
            self._parseNode(parser, ASTLiteralNode(['}']))

        return self

    def __init__(self, lit=None):
        assert isinstance(lit, ASTLiteralNode) or lit == None
        super().__init__()
        self.lit = lit

    def __str__(self):
        return f"Repeat:{super().__str__()}"

class ASTOptionNode(ASTNode):
    """ A node holding an optional group.

    A group enclosed by either:

    - ``[`` or ``(:``;
    - ``]`` or ``:)``.

    May occur either once, or not at all.

    This node has the following variables:

    - Those inherited from |ASTNode|;
    - ``lit`` -- the first literal node in the children list.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTTermNode| |or| |ASTExceptionNode|

    .. rubric:: :ref:`Children <childrenEntry>`

    |ASTLiteralNode| = '[' | '(:', |ASTDefinitionListNode|, |ASTLiteralNode| =
    ']' | ':)'.
    """
    lit = None

    def parse(self, parser):
        self.startLine = parser.line
        self.startColumn = parser.column

        if self.lit == None:
            self._parseNode(parser, ASTLiteralNode(['[']))
        else:
            self.addChild(self.lit, parser.ast)
            self.startLine = self.lit.startLine
            self.startColumn = self.lit.startColumn

        if parser.c.isspace():
            self._parseNode(parser, ASTSpaceNode())

        defList = self._parseNode(parser, ASTDefinitionListNode())

        self.endLine = parser.line
        self.endColumn = parser.column

        lit =self._parseNode(parser, ASTLiteralNode([']', ':)']))

        if lit.data == ':)':
            self.endColumn += 1

        return self

    def __init__(self, lit=None):
        assert isinstance(lit, ASTLiteralNode) or lit == None
        super().__init__()
        self.lit = lit

    def __str__(self):
        return f"Option:{super().__str__()}"

class ASTGroupNode(ASTNode):
    """ A node holding a group.

    A group enclosed by ``(`` and ``)`` can be used to make what are essentially
    inline non-terminals.

    This node has the following variables:

    - Those inherited from |ASTNode|;
    - ``lit`` -- the first literal node in the children list.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTTermNode| |or| |ASTExceptionNode|

    .. rubric:: :ref:`Children <childrenEntry>`

    |ASTLiteralNode| = '(' |ASTDefinitionListNode|, |ASTLiteralNode| = ')'.
    """
    lit = None

    def parse(self, parser):
        self.startLine = parser.line
        self.startColumn = parser.column

        if self.lit == None:
            self._parseNode(parser, ASTLiteralNode(['(']))
        else:
            self.addChild(self.lit, parser.ast)
            self.startLine = self.lit.startLine
            self.startColumn = self.lit.startColumn

        if parser.c.isspace():
            self._parseNode(parser, ASTSpaceNode())

        defList = self._parseNode(parser, ASTDefinitionListNode())

        self.endLine = parser.line
        self.endColumn = parser.column

        self._parseNode(parser, ASTLiteralNode([')']))

        return self

    def __init__(self, lit=None):
        assert isinstance(lit, ASTLiteralNode) or lit == None
        super().__init__()
        self.lit = lit

    def __str__(self):
        return f"Group:{super().__str__()}"

class ASTSpecialNode(ASTNode):
    """ A node holding a special sequence.

    A sequence of text enclosed by ``?`` is considered a special sequence. The
    EBNF spec leaves this as room for defining extension to the language.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |ASTTermNode| |or| |ASTExceptionNode|.

    .. rubric:: :ref:`Children <childrenEntry>`

    |ASTLiteralNode| = '?', |ASTTextNode|, |ASTLiteralNode| = '?'.
    """
    def parse(self, parser):
        self.startLine = parser.line
        self.startColumn = parser.column

        self._parseNode(parser, ASTLiteralNode(['?']))
        self._parseNode(parser, ASTTextNode('?'))

        self.endLine = parser.line
        self.endColumn = parser.column

        self._parseNode(parser, ASTLiteralNode(['?']))

        return self
    def __str__(self):
        return f"Special:{super().__str__()}"

class ASTEmptyNode(ASTNode):
    """A node that holds nothing."""
    def parse(self, parser):
        self.startLine = parser.line
        self.startColumn = parser.column
        self.endLine = parser.line
        self.endColumn = parser.column - 1
        return self

class ASTEmptyTerm(ASTTermNode):
    """A node that is used to represent an empty string as a term."""
    def parse(self, parser):
        self.startLine = parser.line
        self.startColumn = parser.column
        self.endLine = parser.line
        self.endColumn = parser.column - 1
        self._parseNode(parser, ASTEmptyNode())
        return self

