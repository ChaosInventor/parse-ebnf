# SPDX-FileCopyrightText: 2024-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

from collections.abc import Callable

from parse_ebnf import PT, EBNFError, nodes

DEFINITION_SEPARATORS = ['|', '/', '!']
PRODUCT_TERMINATOR_SYMBOLS = [';', '.']
TERMINAL_START_SYMBOLS = ['"', "'", "`"]
PRIMARY_START_SYMBOLS = ['(', '[', '{', '?', *TERMINAL_START_SYMBOLS]

class ParserState:
    """A helper class for parsing, not meant to be used externally, only read.

    Keeps track of the current line and column, ``line`` and ``column``
    respectively, as well as the currently read string, ``c``. It also has a
    reference to the PT it is parsing, ``pt``, and to the read function
    ``readFunc``.

    Has two helper functions for reading input:

     - ``read``
     - ``read_no_eof``

    They help by maintaining ``line``, ``column`` and ``c``.
    """
    pt = None
    readFunc = None
    c = ''
    line = 0
    column = 0

    def read(self, n: int):
        """Reads `n` characters, updates `line`, `column` and `c`, returns self.c"""
        self.c = self.readFunc(n)
        for c in self.c:
            if c == '\n':
                self.line += 1
                self.column = 0
            else:
                self.column += 1

        return self.c
    def read_no_eof(self, n: int, msg: str | None=None):
        """Just like `read` except that it raises a `SyntaxError` with `msg` if
        no characters were read, that is EOF has been reached.
        """
        self.read(n)

        if len(self.c) == 0:
            raise EOFError(self, msg)

        return self.c

    def __init__(self, read: Callable[[int], str], pt: PT):
        """ Create a new parser state for the PT `pt` with the read function
        `read`.
        """
        self.pt = pt
        self.readFunc = read
        self.line = 1
        self.column = 0
        self.read(1)
    def __repr__(self):
        return (f'read={self.readFunc!r}, c={self.c}, line={self.line}, '
                f'column={self.column}, pt={self.pt!r}')

def parse_pt(read: Callable[[int], str]) -> PT:
    """The same as :py:func:`parse_ebnf.parse_from_function`."""
    pt = PT()

    parser = ParserState(read, pt)
    parse_root(parser)

    return pt

def parse_root(parser: ParserState) -> nodes.Root:
    root = nodes.Root()
    parser.pt.root = root
    parser.pt.count = 1
    parser.pt.height = 0
    parser.pt.maxDegree = 0

    root.startLine = parser.line
    root.startColumn = parser.column

    while len(parser.c) > 0:
        if parser.c == '(':
            parse_comment(root, parser)
        elif parser.c.isalpha():
            parse_product(root, parser)
        elif parser.c.isspace():
            parse_space(root, parser)
        else:
            raise UnexpectedCharacterError(
                    parser, 'expected an alphanumeric character, white space or'
                    ' a `(*` literal')

    root.endLine = parser.line
    root.endColumn = parser.column

    return root

def parse_comment(parent: nodes.Node, parser: ParserState,
                 startLit: nodes.Literal = None) -> nodes.Comment:
    comment = nodes.Comment()
    parent.add_child(comment, parser.pt)

    comment.startLine = parser.line
    comment.startColumn = parser.column

    if startLit is None:
        parse_literal(comment, '(*', parser)
    else:
        comment.add_child(startLit, parser.pt)
        comment.startLine = startLit.startLine
        comment.startColumn = startLit.startColumn

    text = None

    #Loop is broken when '*)' is encountered
    while True:
        if parser.c == '*' or parser.c == '(':
            literal = nodes.Literal()
            oc = parser.c

            literal.startLine = parser.line
            literal.startColumn = parser.column

            parser.read_no_eof(1, 'comment not terminated')

            literal.endLine = parser.line
            literal.endColumn = parser.column

            if oc == '*' and parser.c == ')':
                literal.data = '*)'
                comment.add_child(literal, parser.pt)

                break
            elif oc == '(' and parser.c == '*':
                literal.data = '(*'

                parser.read_no_eof(1, 'comment not terminated')
                parse_comment(comment, parser, literal)

                text = None

                continue
            else:
                if text is None:
                    text = nodes.Text()
                    comment.add_child(text, parser.pt)

                    text.startLine = parser.line
                    text.startColumn = parser.column
                    text.endLine = parser.line
                    text.endColumn = parser.column
                text.data += oc
                continue

        if text is None:
            text = nodes.Text()
            comment.add_child(text, parser.pt)

            text.startLine = parser.line
            text.startColumn = parser.column
            text.endLine = parser.line
            text.endColumn = parser.column
        text.data += parser.c
        text.endLine = parser.line
        text.endColumn = parser.column
        parser.read_no_eof(1, 'comment not terminated')

    comment.endLine = parser.line
    comment.endColumn = parser.column

    parser.read(1)

    return comment

def parse_product(parent: nodes.Node, parser: ParserState) -> nodes.Product:
    if not parser.c.isalpha():
        raise UnexpectedCharacterError(parser, 'expected a letter')

    product = nodes.Product()
    parent.add_child(product, parser.pt)

    product.startLine = parser.line
    product.startColumn = parser.column

    identifer, space = parse_identifier(product, parser)
    product.lhs = identifer

    parse_literal(product, '=', parser)

    if parser.c.isspace():
        parse_space(product, parser)

    defList, lit = parse_definition_list(product, parser)

    if lit is not None:
        raise UnexpectedLiteralError(otherLit, parser)
    product.rhs = defList

    lit = parse_literal(product, PRODUCT_TERMINATOR_SYMBOLS, parser)

    product.endLine = lit.endLine
    product.endColumn = lit.endColumn

    return product

def parse_space(parent: nodes.Node, parser: ParserState) -> nodes.Space:
    space = nodes.Space()
    parent.add_child(space, parser.pt)

    if not parser.c.isspace():
        raise NoSpaceError(parser)

    space.startLine = parser.line
    space.startColumn = parser.column

    space.data += parser.c
    space.endLine = parser.line
    space.endColumn = parser.column
    while parser.read(1).isspace():
        space.data += parser.c
        space.endLine = parser.line
        space.endColumn = parser.column

    return space

def parse_literal(parent: nodes.Node, literals: str | list,
                 parser: ParserState) -> nodes.Literal:
    literal = nodes.Literal()
    parent.add_child(literal, parser.pt)

    literal.startLine = parser.line
    literal.startColumn = parser.column

    if isinstance(literals, str):
        read = ''

        for c in literals:
            if parser.c != c:
                raise NoLiteralError(parser, literals, read)

            read += c

            literal.endLine = parser.line
            literal.endColumn = parser.column

            parser.read_no_eof(1, 'reading literal')

        literal.data = read
    else:
        #TODO: Maybe check for duplicate literals?

        read = ''
        potentialMatches = literals[::]
        matches = []

        i = 0
        #Loop is broken when all possible matches are exhausted
        while True:
            matchesCopy = potentialMatches[::]
            for match in matchesCopy:
                if match[i] != parser.c:
                    potentialMatches.remove(match)

            i += 1

            matchesCopy = potentialMatches[::]
            for match in matchesCopy:
                if len(match) <= i:
                    matches.append(match)
                    potentialMatches.remove(match)

            literal.endLine = parser.line
            literal.endColumn = parser.column

            read += parser.c
            if len(potentialMatches) == 0:
                break
            else:
                parser.read_no_eof(1, 'reading literal')

        if len(matches) == 0:
            raise NoLiteralError(parser, literals, read)
        else:
            #TODO: Is having multiple matches impossible given that there are no
            #duplicates or empty strings in the literals list?
            longestMatch = ''
            for match in matches:
                if len(match) > len(longestMatch):
                    longestMatch = match
            literal.data = longestMatch
            if literal.data == read:
                parser.read(1)

    return literal

def parse_identifier(parent: nodes.Node, parser: ParserState) -> nodes.Identifier:
    if not parser.c.isalpha():
        raise UnexpectedCharacterError(parser, 'expected a letter')

    identifier = nodes.Identifier()
    parent.add_child(identifier, parser.pt)

    identifier.startLine = parser.line
    identifier.startColumn = parser.column

    identifier.data += parser.c
    identifier.endLine = parser.line
    identifier.endColumn = parser.column
    parser.read(1)

    hasTrailingWhiteSpace = False
    trailingWhiteSpaceStartLine = 0
    trailingWhiteSpaceStartColumn = 0
    trailingWhiteSpaceEndLine = 0
    trailingWhiteSpaceEndColumn = 0

    while parser.c.isalpha() or parser.c.isnumeric() or parser.c.isspace():
        if parser.c.isspace():
            if hasTrailingWhiteSpace:
                if parser.c == '\n':
                    trailingWhiteSpaceEndColumn = 0
                    trailingWhiteSpaceEndLine += 1
                else:
                    trailingWhiteSpaceEndColumn += 1
            else:
                hasTrailingWhiteSpace = True
                trailingWhiteSpaceStartLine = parser.line
                trailingWhiteSpaceStartColumn = parser.column
                trailingWhiteSpaceEndLine = parser.line
                trailingWhiteSpaceEndColumn = parser.column
        else:
            hasTrailingWhiteSpace = False
            identifier.endLine = parser.line
            identifier.endColumn = parser.column

        identifier.data += parser.c
        parser.read(1)

    #Trailing white space needs to be converted into its own space node. This
    #checks if there is no trailing white space, and if so skips the trimming
    #step.
    if not hasTrailingWhiteSpace:
        return identifier, None

    space = nodes.Space()
    parent.add_child(space, parser.pt)

    space.startLine = trailingWhiteSpaceStartLine
    space.startColumn = trailingWhiteSpaceStartColumn
    space.endLine = trailingWhiteSpaceEndLine
    space.endColumn = trailingWhiteSpaceEndColumn

    space.data = identifier.data[ -(len(identifier.data) - len(identifier.data.rstrip())) :]
    identifier.data = identifier.data.rstrip()

    return identifier, space

def parse_definition_list(parent: nodes.Node, parser: ParserState) -> nodes.DefinitionList:
    definitionList = nodes.DefinitionList()
    parent.add_child(definitionList, parser.pt)

    definitionList.startLine = parser.line
    definitionList.startColumn = parser.column

    #Breaks when it can't handle something. Returns when it encounters the
    #special case of an `\)` literal.
    while True:
        if parser.c.isspace():
            parse_space(definitionList, parser)

        parse_definition(definitionList, parser)

        if parser.c.isspace():
            parse_space(definitionList, parser)

        definitionList.endLine = parser.line
        definitionList.endColumn = parser.column - 1

        if parser.c in DEFINITION_SEPARATORS:
            #Special case for alternate '}'
            if parser.c == '/':
                lit = nodes.Literal()

                lit.startLine = parser.line
                lit.startColumn = parser.column
                lit.endLine = parser.line
                lit.endColumn = parser.column

                parser.read_no_eof(1, 'definition list not terminated')
                if parser.c == ')':
                    lit.data = '/)'
                    lit.endColumn = parser.column

                    definitionList.endLine = parser.line
                    definitionList.endColumn = parser.column - 2

                    parser.read(1)
                    return definitionList, lit
                else:
                    lit.data = '/'
                    definitionList.add_child(lit, parser.pt)
            else:
                parse_literal(definitionList, DEFINITION_SEPARATORS, parser)
        else:
            break

    return definitionList, None

def parse_definition(parent: nodes.Node, parser: ParserState) -> nodes.DefinitionList:
    definition = nodes.Definition()
    parent.add_child(definition, parser.pt)

    definition.startLine = parser.line
    definition.startColumn = parser.column

    #Tracks the current term, used to detected when to parse empty string terms
    #and when terms aren't delimited.
    term = None
    #Breaks when it can't handle something
    while True:
        if len(parser.c) == 0:
            raise EOFError(parser,
                           f'definition started at '
                           f'{definition.startLine},{definition.startColumn} '
                           f'not terminated'
                           )

        if parser.c.isspace():
            parse_space(definition, parser)
        elif parser.c.isalpha() or parser.c.isnumeric() or parser.c in PRIMARY_START_SYMBOLS:
            if term is not None:
                raise UndelimitedTermError(term, parser)
            term = parse_term(definition, parser)
        elif parser.c == ',':
            if term is None:
                parse_empty_term(definition, parser)

            parse_literal(definition, ',', parser)
            term = None
        else:
            #Let the parent handle it
            break

    if term is None:
        parse_empty_term(definition, parser)
    definition.endLine = parser.line
    definition.endColumn = parser.column - 1
    return definition

def parse_term(parent: nodes.Node, parser: ParserState) -> nodes.Term:
    term = nodes.Term()
    parent.add_child(term, parser.pt)

    term.startLine = parser.line
    term.startColumn = parser.column

    #Breaks when it can't handle something
    while True:
        if parser.c.isspace():
            parse_space(term, parser)
        elif parser.c.isnumeric():
            if term.repetition is not None:
                raise MultipleTermRepetitions(term, parser)

            term.repetition = parse_repetition(term, parser)
        elif parser.c == '-':
            if term.exception is not None:
                raise MultipleTermExceptions(term, parser)

            parse_literal(term, '-', parser)
            term.exception = parse_exception(term, parser)
        elif parser.c.isalpha() or parser.c in PRIMARY_START_SYMBOLS:
            if term.primary is not None:
                raise MultipleTermPrimariesError(term, parser)

            term.primary = parse_primary(term, parser)
        else:
            #Let the parent handle it
            break

    if term.primary is None:
        term.primary = parse_empty_string(term, parser)

    term.endLine = term.children[-1].endLine
    term.endColumn = term.children[-1].endColumn
    return term

def parse_repetition(parent: nodes.Node, parser: ParserState) -> nodes.Repetition:
    repetition = nodes.Repetition()
    parent.add_child(repetition, parser.pt)

    repetition.startLine = parser.line
    repetition.startColumn = parser.column

    parse_number(repetition, parser)

    if parser.c.isspace():
        parse_space(repetition, parser)

    repetition.endLine = parser.line
    repetition.endColumn = parser.column
    parse_literal(repetition, '*', parser)

    return repetition

def parse_exception(parent: nodes.Node, parser: ParserState) -> nodes.Exception:
    exception = nodes.Exception()
    parent.add_child(exception, parser.pt)

    exception.startLine = parser.line
    exception.startColumn = parser.column

    while True:
        if parser.c.isspace():
            parse_space(exception, parser)
        elif parser.c.isalpha() or parser.c in PRIMARY_START_SYMBOLS:
            exception.primary = parse_primary(exception, parser)
        else:
            #Let the parent handle it
            break

    if exception.primary is None:
        exception.primary = parse_empty_string(exception, parser)

    exception.endLine = exception.children[-1].endLine
    exception.endColumn = exception.children[-1].endColumn
    return exception

def parse_primary(parent: nodes.Node, parser: ParserState) -> nodes.Primary:
    if parser.c.isalpha() or parser.c in PRIMARY_START_SYMBOLS:
        if parser.c.isalpha():
            identifier, space = parse_identifier(parent, parser)
            return identifier
        elif parser.c in TERMINAL_START_SYMBOLS:
            return parse_terminal(parent, parser)
        elif parser.c == '{':
            return parse_repeat(parent, None, parser)
        elif parser.c == '[':
            return parse_option(parent, None, parser)
        elif parser.c == '(':
            lit = nodes.Literal()

            lit.startLine = parser.line
            lit.startColumn = parser.column
            lit.endLine = parser.line
            lit.endColumn = parser.column

            lit.data += '('

            parser.read_no_eof(1, 'reading primary')

            if parser.c in ['/', ':']:
                lit.data += parser.c
                lit.endColumn = parser.column

                oc = parser.c
                parser.read(1)

                if oc == '/':
                    return parse_repeat(parent, lit, parser)
                elif oc == ':':
                    return parse_option(parent, lit, parser)
                else:
                    raise ParsingError('Bug! Unreachable', parser)
            else:
                return parse_group(parent, lit, parser)
        elif parser.c == '?':
            return parse_special(parent, parser)
        else:
            raise ParsingError('Bug! Unreachable', parser)
    else:
        raise UnexpectedCharacterError(parser, f'expected a letter or one of {PRIMARY_START_SYMBOLS}')

def parse_number(parent: nodes.Node, parser: ParserState) -> nodes.Number:
    number = nodes.Number()
    parent.add_child(number, parser.pt)

    number.startLine = parser.line
    number.startColumn = parser.column

    if not parser.c.isnumeric():
        raise UnexpectedCharacterError(parser, 'expected a number')

    number.data += parser.c
    number.endLine = parser.line
    number.endColumn = parser.column
    while parser.read(1).isnumeric():
        number.data += parser.c
        number.endLine = parser.line
        number.endColumn = parser.column

    return number

def parse_empty_term(parent: nodes.Node, parser: ParserState) -> nodes.Term:
    term = nodes.Term()
    parent.add_child(term, parser.pt)

    term.startLine = parser.line
    term.endLine = parser.line
    term.startColumn = parser.column
    term.endColumn = parser.column - 1

    term.primary = parse_empty_string(term, parser)

    return term

def parse_terminal(parent: nodes.Node, parser: ParserState) -> nodes.Terminal:
    if parser.c not in TERMINAL_START_SYMBOLS:
        raise UnexpectedCharacterError(parser,
                                       f'one of '
                                       f'{TERMINAL_START_SYMBOLS}'
                                       )

    terminal = nodes.Terminal()
    parent.add_child(terminal, parser.pt)

    terminal.startLine = parser.line
    terminal.startColumn = parser.column

    lit = parse_literal(terminal, parser.c, parser)

    text = nodes.Text()
    terminal.add_child(text, parser.pt)

    text.startLine = parser.line
    text.startColumn = parser.column

    while parser.c != lit.data:
        text.data += parser.c
        parser.read_no_eof(1, 'reading terminal')

    text.endLine = parser.line
    text.endColumn = parser.column - 1

    terminal.endLine = parser.line
    terminal.endColumn = parser.column

    parse_literal(terminal, lit.data, parser)

    return terminal

def parse_repeat(parent: nodes.Node, lit: nodes.Literal | None,
                parser: ParserState) -> nodes.Repeat:
    repeat = nodes.Repeat()
    parent.add_child(repeat, parser.pt)

    repeat.startLine = parser.line
    repeat.startColumn = parser.column

    if lit is None:
        repeat.lit = parse_literal(repeat, ['{', '(/'], parser)
    else:
        repeat.add_child(lit, parser.pt)
        repeat.startLine = lit.startLine
        repeat.startColumn = lit.startColumn
        repeat.lit = lit

    if parser.c.isspace():
        parse_space(repeat, parser)

    defList, lit = parse_definition_list(repeat, parser)

    if lit is None:
        repeat.endLine = parser.line
        repeat.endColumn = parser.column
        #No need to check for '/)' since the definition list would have parsed
        #it if it were there.
        parse_literal(repeat, '}', parser)
    else:
        repeat.endLine = lit.endLine
        repeat.endColumn = lit.endColumn
        repeat.add_child(lit, parser.pt)

    return repeat

def parse_option(parent: nodes.Node, lit: nodes.Literal | None,
                parser: ParserState) -> nodes.Option:
    option = nodes.Option()
    parent.add_child(option, parser.pt)

    option.startLine = parser.line
    option.startColumn = parser.column

    if lit is None:
        option.lit = parse_literal(option, ['(:', '['], parser)
    else:
        option.add_child(lit, parser.pt)
        option.startLine = lit.startLine
        option.startColumn = lit.startColumn
        option.lit = lit

    if parser.c.isspace():
        parse_space(option, parser)

    defList, otherLit = parse_definition_list(option, parser)

    if otherLit is not None:
        raise UnexpectedLiteralError(otherLit, parser)

    option.endLine = parser.line
    option.endColumn = parser.column

    lit = parse_literal(option, [']', ':)'], parser)

    if lit.data == ':)':
        option.endColumn += 1

    return option

def parse_group(parent: nodes.Node, lit: nodes.Literal| None,
               parser: ParserState) -> nodes.Group:
    group = nodes.Group()
    parent.add_child(group, parser.pt)

    group.startLine = parser.line
    group.startColumn = parser.column

    if lit is None:
        group.lit = parse_literal(group, '(', parser)
    else:
        group.add_child(lit, parser.pt)
        group.startLine = lit.startLine
        group.startColumn = lit.startColumn
        group.lit = lit

    if parser.c.isspace():
        parse_space(group, parser)

    defList, otherLit = parse_definition_list(group, parser)

    if otherLit is not None:
        raise UnexpectedLiteralError(otherLit, parser)

    group.endLine = parser.line
    group.endColumn = parser.column

    parse_literal(group, ')', parser)

    return group

def parse_special(parent: nodes.Node, parser: ParserState) -> nodes.Special:
    special = nodes.Special()
    parent.add_child(special, parser.pt)

    special.startLine = parser.line
    special.startColumn = parser.column

    parse_literal(special, '?', parser)

    text = nodes.Text()
    text.startLine = parser.line
    text.startColumn = parser.column
    text.endLine = parser.line
    text.endColumn = parser.column - 1
    special.add_child(text, parser.pt)
    while parser.c != '?':
        text.data += parser.c
        text.endLine = parser.line
        text.endColumn = parser.column
        parser.read_no_eof(1, 'reading special')

    special.endLine = parser.line
    special.endColumn = parser.column

    parse_literal(special, '?', parser)

    return special

def parse_empty_string(parent: nodes.Node, parser: ParserState) -> nodes.EmptyString:
    emptyString = nodes.EmptyString()
    parent.add_child(emptyString, parser.pt)

    emptyString.startLine = parser.line
    emptyString.startColumn = parser.column
    emptyString.endLine = parser.line
    emptyString.endColumn = parser.column - 1

    return emptyString


class ParsingError(EBNFError):
    """Base class of all parsing related errors.

    Each instance of this class has a variable named ``parser`` that represents
    the :py:class:`parsing state <parse_ebnf.parsing.ParserState>` at the time
    the error occurred. With that you can get both the line and column of the
    error along with the :ref:`partial parse tree <partial>`.
    """
    def __init__(self, message, parser: ParserState):
        super().__init__(message)
        self.parser = parser

class EOFError(ParsingError):
    """An end of file was reached in an unexpected place."""
    def __init__(self, parser: ParserState, reason: str | None = None):
        if reason is None:
            super().__init__(f'Did not expect EOF at {parser.line},'
                             f'{parser.column}', parser
                             )
        else:
            super().__init__(f'Did not expect EOF at {parser.line},'
                             f'{parser.column}, {reason}', parser
                             )

class UnexpectedCharacterError(ParsingError):
    """An unexpected character occurred during parsing.

    The unexpected character can be found in ``parser.c``.
    """
    def __init__(self, parser: ParserState, expected: str | None=None):
        if expected is None:
            super().__init__(f'Did not expect character `{parser.c}` at '
                             f'{parser.line},{parser.column}', parser
                             )
        else:
            super().__init__(f'Did not expect character `{parser.c}` at '
                             f'{parser.line},{parser.column}, {expected}', parser
                             )

class NoSpaceError(ParsingError):
    """Expected a space character at the current line and column."""
    def __init__(self, parser: ParserState):
        super().__init__(f'Expected a space character at '
                         f'{parser.line},{parser.column}, but found '
                         f'`{parser.c}`', parser
                         )

class NoLiteralError(ParsingError):
    """Could not match a literal.

    The expected literal or literals can be found in the instance variable
    ``literals`` that may be a string or list of strings. The instance variable
    ``read`` contains the characters that were read whilst matching the given
    literal.
    """
    def __init__(self, parser: ParserState, literals: list | str, read: str):
        super().__init__(f'Could not match {literals} at '
                         f'{parser.line},{parser.column}', parser
                         )
        self.literals = literals
        self.read = read

class UndelimitedTermError(ParsingError):
    """The previous |Term| was not delimited with a comma.

    The previous term can be found in the instance variable ``term``.
    """
    def __init__(self, term: nodes.Term, parser: ParserState):
        super().__init__(f'Start of another term at '
                         f'{parser.line},{parser.column} before previous term '
                         f'at {term.startLine},{term.startColumn} terminated',
                         parser
                         )
        self.term = term

class MultipleTermRepetitions(ParsingError):
    """Multiple |Repetition| nodes were parsed for a single |Term|

    The term in question can be found in the instance variable ``term``.
    """
    def __init__(self, term: nodes.Term, parser: ParserState):
        super().__init__(f'Term can only have one repetition, another defined '
                         f'at {parser.line},{parser.column}, last one defined '
                         f'at {term.repetition.startLine},'
                         f'{term.repetition.startColumn}',
                         parser
                         )
        self.term = term

class MultipleTermExceptions(ParsingError):
    """Multiple |Exception| nodes were parsed for a single |Term|

    The term in question can be found in the instance variable ``term``.
    """
    def __init__(self, term: nodes.Term, parser: ParserState):
        super().__init__(f'Unexpected `-`, term started at '
                         f'{term.startLine},{term.startColumn} already has an '
                         f'exception defined at '
                         f'{term.exception.startLine},'
                         f'{term.exception.startColumn}',
                         parser
                         )
        self.term = term

class MultipleTermPrimariesError(ParsingError):
    """Multiple |Primary| nodes were parsed for a single |Term|

    The term in question can be found in the instance variable ``term``.
    """
    def __init__(self, term: nodes.Term, parser: ParserState):
        super().__init__(f'Term started at {term.startLine},{term.startColumn} '
                         f'can only have one primary, however another defined '
                         f'at {parser.line},{parser.column}',
                         parser
                         )
        self.term = term

class UnexpectedLiteralError(ParsingError):
    """Did not expect to parser a literal.

    The literal in question can be found in the instance variable ``literal``.
    """
    def __init__(self, lit: nodes.Literal, parser: ParserState):
            super().__init__(f'Did not expect literal `{lit.data}` at '
                             f'{lit.startLine},{lit.startColumn}', parser
                             )
            self.literal = lit
