class Node:
    """Base class of all PT nodes.

    PT nodes differ only in what nodes are their ``parent`` and which nodes
    are their ``children``, more info at the :doc:`tree structure <tree>`.
    This node type in particular is not used in the |PT|, it only serves as a
    base class for all other node types. Using ``isinstance`` you can resolve
    a node's type.

    Contains the following variables:

    - ``parent`` -- the parent node of this node. It is ``None`` only for
      |Root|.
    - ``children`` -- a list of this node's children. Empty only for instance of
      |Text|.
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
    - if `startColumn` > `endColumn`: str(node) == '' else: `endColumn` >= 0

    .. note :: The end coordinates also take into account child nodes. The
       children's text is also counted as the parent's text.
    """
    parent = None
    children = []
    depth = 0
    startLine = 0
    startColumn = 0
    endLine = 0
    endColumn = 0

    def unparse(self, write):
        write(str(self))

    def addChild(self, node, pt):
        self.children.append(node)
        node.parent = self
        node.depth = self.depth + 1

        pt.count += 1
        pt.height = node.depth if node.depth > pt.height else pt.height
        pt.maxDegree = len(self.children) if len(self.children) > pt.maxDegree else pt.maxDegree

        return node
    def write(self, write, depth=0):
        write(repr(self))
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
    def __repr__(self):
        ret = f"{type(self).__name__}:{self.startLine},{self.startColumn}-{self.endLine},{self.endColumn}\n"
        for child in self.children:
            ret = ''.join([ret, '\t' * child.depth])
            ret += repr(child)
        return ret
    def __str__(self):
        ret = ''
        for child in self:
            ret += str(child)
        return ret

    def _parseNode(self, parser, node):
        self.addChild(node, parser.pt)
        return node.parse(parser)

class Root(Node):
    """ The root PT node.

    .. rubric:: :ref:`Parent type <parentEntry>`

    ``None``

    .. rubric:: :ref:`Children <childrenEntry>`

    (|Product| |or| |Comment| |or| |Space|)\ |any|

    """


class Text(Node):
    """ Base class for leaf nodes.

    This node is a base class for all leaf nodes, nodes whose ``children`` list
    is empty.

    .. note:: Only leafs nodes contain text data in the tree.

    This node has the following variables:

    - Variables inherited from |Node|;
    - ``data`` -- the text content of the node, a string.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Terminal| |or| |Space|.

    .. rubric:: :ref:`Children <childrenEntry>`

    ``None`` -- These nodes and their derived classes are always leaf nodes.

    """
    data = ''

    def __init__(self, start=None, data=''):
        super().__init__()
        self.data = data
    def __repr__(self):
        return f'({self.data})' + super().__repr__()
    def __str__(self):
        return self.data
class Comment(Node):
    """Nodes holding EBNF comments.

    Comments in EBNF are enclosed by ``(*``, ``*)`` pairs. Nesting is allowed.

    The ``data`` string does **NOT** contain the enclosing comment markers.
    Nested comment markers are included however. ``repr`` returns a proper
    comment string.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Root|

    .. rubric:: :ref:`Children <childrenEntry>`

    ``[]``, leaf node, see |Text|.

    """

class Space(Text):
    """Node holding whitespace.

    .. rubric:: :ref:`Parent type <parentEntry>`

    ``Any``, just about every node that is not a leaf node holds this node.

    .. rubric:: :ref:`Children <childrenEntry>`

    ``None``, it is a leaf node, see |Text|.
    """
    def __init__(self, data=''):
        super().__init__(None, data)
class Literal(Text):
    """Node holding one or more characters.

    The actual character sequence depends on the parent. The parent nodes have
    documentation pertaining to the exact sequence.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Product| |or| |DefinitionList| |or| |Definition| |or|
    |Term| |or| |Exception| |or| |Repetition| |or|
    |Terminal| |or| |Repeat| |or| |Option| |or|
    |Group| |or| |Space|.

    .. rubric:: :ref:`Children <childrenEntry>`

    ``None``, it is a leaf node, see |Text|.
    """

    def __init__(self, data=''):
        super().__init__(data)

class Product(Node):
    """ A node holding a product.

    A product is a grammar rule, those of the form:

    ``something = another | third, 'a';``

    This node has the following variables:

    - Those inherited from |Node|;
    - ``lhs``, the left hand side of the rule, the first |Identifier| of
      the children;
    - ``rhs``, the right had side of the rule, the first |DefinitionList|
      of the children.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Root|.

    .. rubric:: :ref:`Children <childrenEntry>`

    |Space|\ |maybe|, |Identifier|, |Space|\ |maybe|,
    |Literal| = '=', |Space|\ |maybe|, |DefinitionList|,
    |Space|\ |maybe|, |Literal| = ';' | '.'
    """
    lhs = None
    rhs = None

    def __init__(self, lhs=None, rhs=None, pt=None):
        super().__init__()
        if lhs != None or rhs != None:
            assert isinstance(pt, PT), f"Expected an abstract syntax tree, not a {pt.__class__}"
        if lhs != None:
            self.lhs = lhs
            self.addChild(lhs, pt)
        if rhs != None:
            self.rhs = rhs
            self.addChild(rhs, pt)

class DefinitionList(Node):
    """ Node containing a list of definitions.

    Definitions are the lists of concatenations. Definitions are placed
    in-between alterations symbols. This node can be seen as holding all
    alternatives of a rule.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Product| |or| |Repetition| |or| |Option| |or|
    |Group|.

    .. rubric:: :ref:`Children <childrenEntry>`

    |Space|\ |maybe|, (|Definition|, |Space|\ |maybe|,
    |Literal| = '|' | '/' | '!')\ |any|, |Space|\ |maybe|.
    """

class Definition(Node):
    """A node holding a definition.

    A definition is the list of concatenations on the right hand side of a rule.
    This node can be seen as having a sequence that a rule needs to match.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |DefinitionList|

    .. rubric:: :ref:`Children <childrenEntry>`

    |Space|\ |maybe|, ((|Term| |or| |EmptyTerm|), |Space|\ |maybe|,
    |Literal| = ',', |Space|\ |maybe|)\ |any|.

    """

class Term(Node):
    """ Node holding a single term.

    Terms are values that a rule can take, they may be either:

    - Terminals;
    - Non-terminals;
    - Groups.

    This node has the following variables:

    - Those inherited from |Node|;
    - ``repetition`` -- an |Repetition|, the one in the children list;
    - ``primary`` -- the term that this node is defined as, the one in the
      children list, may either be:

        - |Terminal|;
        - |Identifier|;
        - |Group|;
        - |Repeat|;
        - |Option|;
        - |Special|.

    - ``exception`` -- an |Exception|, the one in the children list.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Definition|

    .. rubric:: :ref:`Children <childrenEntry>`

    |Space|\ |maybe|, |Repetition|\ |maybe|, |Space|\
    |maybe|, (|Identifier| |or| |Terminal| |or| |Repeat|
    |or| |Option| |or| |Special| |or| |Group| |or|
    |Empty|), (|Space|\ |maybe|, |Literal| = '-',
    |Exception|)\ |maybe|.

    """
    repetition = None
    primary = None
    exception = None

    def __init__(self, pt=None, repetition=None, primary=None, exception=None):
        assert repetition == None or isinstance(repetition, Repetition), f"Repetition must be either None or an int, got {repetition}"
        assert isinstance(primary, Node) or primary == None, "A term must have a primary"
        assert isinstance(exception, Term) or exception == None, "Exception must be another term"
        if primary != None or exception != None:
            assert isinstance(pt, PT), "Expected an abstract syntax tree"

        super().__init__()
        self.repetition = repetition
        self.primary = primary
        if primary != None:
            self.addChild(primary, pt)

        self.exception = exception
        if exception != None:
            self.addChild(exception)


class Exception(Node):
    """ A node holding the exception to a term.

    Exceptions are written after a term's primary, prefixed with a ``-``.
    They're terms themselves, except that they don't have exceptions and
    repetitions.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Term|

    .. rubric:: :ref:`Children <childrenEntry>`

    |Space|\ |maybe|, (|Identifier| |or| |Terminal| |or|
    |Repeat| |or| |Option| |or| |Special| |or|
    |Group| |or| |Empty|).

    """
    primary = None

    def __init__(self, pt=None, primary=None):
        assert isinstance(primary, Node) or primary == None, "A term must have a primary"
        if primary != None:
            assert isinstance(pt, PT), "Expected an abstract syntax tree"

        super().__init__()
        self.primary = primary
        if primary != None:
            self.addChild(primary, pt)


class Repetition(Node):
    """A node holding how many times at most a term may be repeated.

    This node has the following variables:

    - Those inherited from |Node|;
    - ``count`` -- an integer denoting the repetition count.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Term|

    .. rubric:: :ref:`Children <childrenEntry>`

    |Space|\ |maybe|, |Literal| = '*', |Space|\ |maybe|.
    """
    count = 0

    def __init__(self, count=0):
        super().__init__()
        self.count = count
    def __str__(self):
        return str(self.count) + super().__str__()

class Primary(Node):
    """ A node holding what a term parses
    TODO:
    """
    pass

class Terminal(Primary):
    """A node holding a terminal.

    Terminals are sequences of characters that are enclosed by either:

    - ``'``;
    - ``"``;
    - ``\```.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Term| |or| |Exception|.

    .. rubric:: :ref:`Children <childrenEntry>`

    |Literal| = '"' | "'" | '`', |Text|, |Literal| = '"' |
    "'" | '`'.
    """
class Repeat(Primary):
    """ A node holding a repeatable group.

    A group enclosed by either:

    - ``{`` or ``(/``;
    - ``}`` or ``/)``.

    May be repeated any number of times, including none.

    This node has the following variables:

    - Those inherited from |Node|;
    - ``lit`` -- the first literal node in the children list.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Term| |or| |Exception|

    .. rubric:: :ref:`Children <childrenEntry>`

    |Literal| = '{' | '(/', |DefinitionList|, |Literal| =
    '}' | '/)'.
    """
    lit = None

    def __init__(self, lit=None):
        assert isinstance(lit, Literal) or lit == None
        super().__init__()
        self.lit = lit

class Option(Primary):
    """ A node holding an optional group.

    A group enclosed by either:

    - ``[`` or ``(:``;
    - ``]`` or ``:)``.

    May occur either once, or not at all.

    This node has the following variables:

    - Those inherited from |Node|;
    - ``lit`` -- the first literal node in the children list.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Term| |or| |Exception|

    .. rubric:: :ref:`Children <childrenEntry>`

    |Literal| = '[' | '(:', |DefinitionList|, |Literal| =
    ']' | ':)'.
    """
    lit = None

    def __init__(self, lit=None):
        assert isinstance(lit, Literal) or lit == None
        super().__init__()
        self.lit = lit

class Group(Primary):
    """ A node holding a group.

    A group enclosed by ``(`` and ``)`` can be used to make what are essentially
    inline non-terminals.

    This node has the following variables:

    - Those inherited from |Node|;
    - ``lit`` -- the first literal node in the children list.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Term| |or| |Exception|

    .. rubric:: :ref:`Children <childrenEntry>`

    |Literal| = '(' |DefinitionList|, |Literal| = ')'.
    """
    lit = None

    def __init__(self, lit=None):
        assert isinstance(lit, Literal) or lit == None
        super().__init__()
        self.lit = lit

class Special(Primary):
    """ A node holding a special sequence.

    A sequence of text enclosed by ``?`` is considered a special sequence. The
    EBNF spec leaves this as room for defining extension to the language.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Term| |or| |Exception|.

    .. rubric:: :ref:`Children <childrenEntry>`

    |Literal| = '?', |Text|, |Literal| = '?'.
    """

class Identifier(Text, Primary):
    """Node holding an identifier.

    Identifiers are alphanumeric string that do not start with a number. They
    do not contain trailing or leading whitespace, however they may contain
    whitespace in the middle.

    .. rubric:: :ref:`Parent type <parentEntry>`

    |Product| |or| |Term| |or| |Exception|.

    .. rubric:: :ref:`Children <childrenEntry>`

    ``None``, it is a leaf node, see |Text|.
    """
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
            space = Space(ret[::-1])

            space.startLine = self.endLine
            space.startColumn = self.endColumn + 1

            space.endLine = space.startLine
            space.endColumn = 0
            onLptLine = True
            for c in ret:
                if c == '\n':
                    space.endLine += 1
                    onLptLine = False
                elif onLptLine:
                    space.endColumn += 1

            if space.startLine == space.endLine:
                space.endColumn = space.startColumn + len(ret) - 1

            return space
        else:
            return None

class EmptyString(Text, Primary):
    """A node that holds nothing."""

