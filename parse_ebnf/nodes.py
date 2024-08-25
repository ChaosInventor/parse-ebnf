# SPDX-FileCopyrightText: 2024-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

class Node:
    """Base class of all PT nodes.

    PT nodes differ only in what nodes are their ``parent`` and which nodes
    are their ``children``, :ref:`see the reference <concreteNodes>`.

    This node type, along with |Leaf| and |Primary|, are not instantiated in the
    |PT|, they serve as abstract base classes.

    This class in particular is the base for all other node types. The intent is
    to use ``isinstance`` to resolve a node's exact type.

    All nodes contain the following variables:

    - ``parent`` -- a |Node| instance that acts as the parent for this node. It
      is ``None`` only for |Root|.
    - ``children`` -- a list of |Node| instances that act as this node's
      children. Every node in this list has its ``parent`` set to this node.
      Empty only for instances of |Leaf|.
    - ``depth`` -- an integer denoting how deep this node is in the tree. The
      root is defined as being at depth 0, it's children at depth 1, their
      children at depth 2, etc.
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

    The following statements are always true:

    - `startLine` >= 0
    - `endLine` >= 0
    - `startColumn` >= 0
    - `startLine` <= `endLine`
    - if `startColumn` > `endColumn` and `startLine` == `endLine`:
      str(node) == '' else: `endColumn` >= 0

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

    def add_child(self, node, pt):
        self.children.append(node)
        node.parent = self
        node.depth = self.depth + 1

        pt.count += 1
        pt.height = node.depth if node.depth > pt.height else pt.height
        pt.maxDegree = len(self.children) if len(self.children) > pt.maxDegree else pt.maxDegree

        return node

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
class Leaf(Node):
    """Base class of all leaf nodes.

    This node is a base class for all leaf nodes, nodes whose ``children`` list
    is empty.

    .. note:: Only leafs nodes contain text data in the tree.

    This node has the following variables:

    - Variables inherited from |Node|;
    - ``data`` -- the text content of the node, a string.
    """
    data = ''

    def __init__(self, data=''):
        super().__init__()
        self.data = data
    def __repr__(self):
        return f'({self.data})' + super().__repr__()
    def __str__(self):
        return self.data
class Primary(Node):
    """A node holding what a term parses.

    This class is mainly meant to tag other nodes that may be primaries for a
    |Term|.

    The current list of primaries is:

    - |Terminal|;
    - |Repeat|;
    - |Option|;
    - |Group|;
    - |Special|;
    - |Identifier|;
    - |EmptyString|.
    """

class Root(Node):
    """The root PT node.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Root.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Root.py
        :lines: 5

    """
class Comment(Node):
    """Nodes holding EBNF comments.

    Comments in EBNF are enclosed by ``(*``, ``*)`` pairs. Nesting is allowed.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Comment.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Comment.py
        :lines: 5

    """
class Product(Node):
    """A node holding a product.

    A product is a grammar rule, those of the form:

    ``something = another | third, 'a';``

    This node has the following variables:

    - Those inherited from |Node|;
    - ``lhs``, the left hand side of the rule, the first |Identifier| of
      the children;
    - ``rhs``, the right had side of the rule, the first |DefinitionList|
      of the children.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Product.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Product.py
        :lines: 5
    """
    lhs = None
    rhs = None
class DefinitionList(Node):
    """Node containing a list of definitions.

    Definitions are the lists of concatenations. Definitions are placed
    in-between alterations symbols. This node can be seen as holding all
    alternatives of a rule.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/DefinitionList.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/DefinitionList.py
        :lines: 5
    """
class Definition(Node):
    """A node holding a definition.

    A definition is the list of concatenations on the right hand side of a rule.
    This node can be seen as having a sequence that a rule needs to match.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Definition.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Definition.py
        :lines: 5

    """
class Term(Node):
    """Node holding a single term.

    Terms are values that a rule can take, they may be either:

    - Terminals;
    - Non-terminals;
    - Groups.

    This node has the following variables:

    - Those inherited from |Node|;
    - ``repetition`` -- a |Repetition|, the one in the children list;
    - ``primary`` -- what is to be parsed, the one in the children list, always
      an instance of |Primary|.

    - ``exception`` -- an |Exception|, the one in the children list.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Term.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Term.py
        :lines: 5

    """
    repetition = None
    primary = None
    exception = None
class Exception(Node):
    """A node holding the exception to a term.

    Exceptions are written after a term's primary, prefixed with a ``-``.
    They're terms themselves, except that they don't have exceptions and
    repetitions.

    This node has the following variables:

    - Those inherited from |Node|;
    - ``primary`` -- what is to be excluded from parsing, the one in the
      children list, always an instance of |Primary|.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Exception.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Exception.py
        :lines: 5

    """
    primary = None
class Repetition(Node):
    """A node holding how many times at most a term may be repeated.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Repetition.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Repetition.py
        :lines: 5
    """

class Terminal(Primary):
    r"""A node holding a terminal.

    Terminals are sequences of characters that are enclosed by either:

    - ``'``;
    - ``"``;
    - ``\```.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Terminal.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Terminal.py
        :lines: 5
    """
class Repeat(Primary):
    """A node holding a repeatable group.

    A group enclosed by either:

    - ``{`` or ``(/``;
    - ``}`` or ``/)``.

    May be repeated any number of times, including none.

    This node has the following variables:

    - Those inherited from |Node|;
    - ``lit`` -- the first literal node in the children list.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Repeat.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Repeat.py
        :lines: 5
    """
    lit = None

    def __init__(self, lit=None):
        assert isinstance(lit, Literal) or lit is None
        super().__init__()
        self.lit = lit
class Option(Primary):
    """A node holding an optional group.

    A group enclosed by either:

    - ``[`` or ``(:``;
    - ``]`` or ``:)``.

    May occur either once, or not at all.

    This node has the following variables:

    - Those inherited from |Node|;
    - ``lit`` -- the first literal node in the children list.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Option.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Option.py
        :lines: 5
    """
    lit = None

    def __init__(self, lit=None):
        assert isinstance(lit, Literal) or lit is None
        super().__init__()
        self.lit = lit
class Group(Primary):
    """A node holding a group.

    A group enclosed by ``(`` and ``)`` can be used to make what are essentially
    inline non-terminals.

    This node has the following variables:

    - Those inherited from |Node|;
    - ``lit`` -- the first literal node in the children list.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Group.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Group.py
        :lines: 5
    """
    lit = None

    def __init__(self, lit=None):
        assert isinstance(lit, Literal) or lit is None
        super().__init__()
        self.lit = lit
class Special(Primary):
    """A node holding a special sequence.

    A sequence of text enclosed by ``?`` is considered a special sequence. The
    EBNF spec leaves this as room for defining extensions to the language.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Special.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Special.py
        :lines: 5
    """

class Identifier(Leaf, Primary):
    """Node holding an identifier.

    Identifiers are alphanumeric string that do not start with a number. They
    do not contain trailing or leading whitespace, however they may contain
    whitespace in the middle.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Identifier.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Identifier.py
        :lines: 5
    """
class EmptyString(Leaf, Primary):
    """A node that represents the empty string.

    EBNF does not have a symbol for the empty string, instead it is represented
    by another empty string.

    The ``data`` instance variable is always an empty string.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/EmptyString.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/EmptyString.py
        :lines: 5
    """

class Text(Leaf):
    """Node holding text.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Text.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Text.py
        :lines: 5

    """
class Space(Leaf):
    """Node holding whitespace.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Space.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Space.py
        :lines: 5
    """
class Literal(Leaf):
    """Node holding one or more characters.

    The actual character sequence depends on the parent. The parent nodes have
    documentation pertaining to the exact sequence.

    .. rubric:: :ref:`Parent type <parentEntry>`

    .. literalinclude:: /tree_structure/Literal.py
        :lines: 4

    .. rubric:: :ref:`Children <childrenEntry>`

    .. literalinclude:: /tree_structure/Literal.py
        :lines: 5
    """
class Number(Leaf):
    """Node holding a positive integer.

    The number is stored as a string in the ``data`` variable. Use the instance
    function ``to_int`` to convert it to an integer.
    """
    def to_int():
        return int(self.data)
