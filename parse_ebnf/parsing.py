from collections.abc import Callable
from parse_ebnf import PT, nodes, EBNFError

DEFINITION_SEPARATORS = ['|', '/', '!']
PRODUCT_TERMINATOR_SYMBOLS = [';', '.']
TERMINAL_START_SYMBOLS = ['"', "'", "`"]
PRIMARY_START_SYMBOLS = ['(', '[', '{', '?', *TERMINAL_START_SYMBOLS]

class ParserState:
    """A helper class for parsing, not meant to be used externally.

    Keeps track of the current line and column, `line` and `column`
    respectively, as well as the currently read string, `c`. It also has a
    reference to the PT it belongs, `pt`, and to the read function `readFunc`

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
    def readNoEOF(self, n: int, msg: str | None=None):
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
        return (f'read={repr(self.readFunc)}, c={self.c}, line={self.line}, '
                f'column={self.column}, pt={repr(self.pt)}')

def parsePT(read: Callable[[int], str]) -> PT:
    pt = PT()

    parser = ParserState(read, pt)
    parseRoot(parser)

    return pt

def parseRoot(parser: ParserState) -> nodes.Root:
    root = nodes.Root()
    parser.pt.root = root
    parser.pt.count = 1
    parser.pt.height = 0
    parser.pt.maxDegree = 0

    root.startLine = parser.line
    root.startColumn = parser.column

    while len(parser.c) > 0:
        if parser.c == '(':
            parseComment(root, parser)
        elif parser.c.isalpha():
            parseProduct(root, parser)
        elif parser.c.isspace():
            parseSpace(root, parser)
        else:
            raise UnexpectedCharacterError(
                    parser, 'expected an alphanumeric character, white space or'
                    ' a `(*` literal')

    root.endLine = parser.line
    root.endColumn = parser.column

    return root

def parseComment(parent: nodes.Node, parser: ParserState,
                 startLit: nodes.Literal = None) -> nodes.Comment:
    comment = nodes.Comment()
    parent.addChild(comment, parser.pt)

    comment.startLine = parser.line
    comment.startColumn = parser.column

    if startLit is None:
        parseLiteral(comment, '(*', parser)
    else:
        comment.addChild(startLit, parser.pt)
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

            parser.readNoEOF(1, 'comment not terminated')

            literal.endLine = parser.line
            literal.endColumn = parser.column

            if oc == '*' and parser.c == ')':
                literal.data = '*)'
                comment.addChild(literal, parser.pt)

                break
            elif oc == '(' and parser.c == '*':
                literal.data = '(*'

                parser.readNoEOF(1, 'comment not terminated')
                parseComment(comment, parser, literal)

                text = None

                continue
            else:
                if text is None:
                    text = nodes.Text()
                    comment.addChild(text, parser.pt)

                    text.startLine = parser.line
                    text.startColumn = parser.column
                    text.endLine = parser.line
                    text.endColumn = parser.column
                text.data += oc
                continue

        if text is None:
            text = nodes.Text()
            comment.addChild(text, parser.pt)

            text.startLine = parser.line
            text.startColumn = parser.column
            text.endLine = parser.line
            text.endColumn = parser.column
        text.data += parser.c
        text.endLine = parser.line
        text.endColumn = parser.column
        parser.readNoEOF(1, 'comment not terminated')

    comment.endLine = parser.line
    comment.endColumn = parser.column

    parser.read(1)

    return comment

def parseProduct(parent: nodes.Node, parser: ParserState) -> nodes.Product:
    if not parser.c.isalpha():
        raise UnexpectedCharacterError(parser, 'expected a letter')

    product = nodes.Product()
    parent.addChild(product, parser.pt)

    product.startLine = parser.line
    product.startColumn = parser.column

    if parser.c.isspace():
        parseSpace(product, parser)

    parseIdentifier(product, parser)

    parseLiteral(product, '=', parser)

    if parser.c.isspace():
        parseSpace(product, parser)

    defList, lit = parseDefinitionList(product, parser)

    if lit is not None:
        raise UnexpectedLiteralError(otherLit, parser)

    lit = parseLiteral(product, PRODUCT_TERMINATOR_SYMBOLS, parser)

    product.endLine = lit.endLine
    product.endColumn = lit.endColumn

    return product

def parseSpace(parent: nodes.Node, parser: ParserState) -> nodes.Space:
    space = nodes.Space()
    parent.addChild(space, parser.pt)

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

def parseLiteral(parent: nodes.Node, literals: str | list,
                 parser: ParserState) -> nodes.Literal:
    literal = nodes.Literal()
    parent.addChild(literal, parser.pt)

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

            parser.readNoEOF(1, 'reading literal')

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
                parser.readNoEOF(1, 'reading literal')

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

def parseIdentifier(parent: nodes.Node, parser: ParserState) -> nodes.Identifier:
    if not parser.c.isalpha():
        raise UnexpectedCharacterError(parser, 'expected a letter')

    identifier = nodes.Identifier()
    parent.addChild(identifier, parser.pt)

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
        return identifier

    space = nodes.Space()
    parent.addChild(space, parser.pt)

    space.startLine = trailingWhiteSpaceStartLine
    space.startColumn = trailingWhiteSpaceStartColumn
    space.endLine = trailingWhiteSpaceEndLine
    space.endColumn = trailingWhiteSpaceEndColumn

    space.data = identifier.data[ -(len(identifier.data) - len(identifier.data.rstrip())) :]
    identifier.data = identifier.data.rstrip()

    return identifier, space

def parseDefinitionList(parent: nodes.Node, parser: ParserState) -> nodes.DefinitionList:
    definitionList = nodes.DefinitionList()
    parent.addChild(definitionList, parser.pt)

    definitionList.startLine = parser.line
    definitionList.startColumn = parser.column

    #Breaks when it can't handle something. Returns when it encounters the
    #special case of an `\)` literal.
    while True:
        if parser.c.isspace():
            parseSpace(definitionList, parser)

        parseDefinition(definitionList, parser)

        if parser.c.isspace():
            parseSpace(definitionList, parser)

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

                parser.readNoEOF(1, 'definition list not terminated')
                if parser.c == ')':
                    lit.data = '/)'
                    lit.endColumn = parser.column

                    definitionList.endLine = parser.line
                    definitionList.endColumn = parser.column - 2

                    parser.read(1)
                    return definitionList, lit
                else:
                    lit.data = '/'
                    definitionList.addChild(lit, parser.pt)
            else:
                parseLiteral(definitionList, DEFINITION_SEPARATORS, parser)
        else:
            break

    return definitionList, None

def parseDefinition(parent: nodes.Node, parser: ParserState) -> nodes.DefinitionList:
    definition = nodes.Definition()
    parent.addChild(definition, parser.pt)

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
            parseSpace(definition, parser)
        elif parser.c.isalpha() or parser.c.isnumeric() or parser.c in PRIMARY_START_SYMBOLS:
            if term != None:
                raise UndelimitedTermError(term, parser)
            term = parseTerm(definition, parser)
        elif parser.c == ',':
            if term == None:
                parseEmptyTerm(definition, parser)

            parseLiteral(definition, ',', parser)
            term = None
        else:
            #Let the parent handle it
            break;

    if term == None:
        parseEmptyTerm(definition, parser)
    definition.endLine = parser.line
    definition.endColumn = parser.column - 1
    return definition

def parseTerm(parent: nodes.Node, parser: ParserState) -> nodes.Term:
    term = nodes.Term()
    parent.addChild(term, parser.pt)

    term.startLine = parser.line
    term.startColumn = parser.column

    #Breaks when it can't handle something
    while True:
        if parser.c.isspace():
            parseSpace(term, parser)
        elif parser.c.isnumeric():
            if term.repetition != None:
                raise MultipleTermRepetitions(term, parser)

            term.repetition = parseRepetition(term, parser)
        elif parser.c == '-':
            if term.exception != None:
                raise MultipleTermExceptions(term, parser)

            parseLiteral(term, '-', parser)
            term.exception = parseException(term, parser)
        elif parser.c.isalpha() or parser.c in PRIMARY_START_SYMBOLS:
            if term.primary != None:
                raise MultipleTermPrimariesError(term, parser)

            term.primary = parsePrimary(term, parser)
        else:
            #Let the parent handle it
            break

    if term.primary == None:
        term.primary = parseEmptyString(term, parser)

    term.endLine = term.children[-1].endLine
    term.endColumn = term.children[-1].endColumn
    return term

def parseRepetition(parent: nodes.Node, parser: ParserState) -> nodes.Repetition:
    if not parser.c.isnumeric():
        raise UnexpectedCharacterError(parser, 'expected a number')

    repetition = nodes.Repetition()
    parent.addChild(repetition, parser.pt)

    repetition.startLine = parser.line
    repetition.startColumn = parser.column

    num = parser.c
    while parser.readNoEOF(1, 'reading integer').isnumeric():
        num += parser.c
    repetition.count = int(num)

    if parser.c.isspace():
        parseSpace(repetition, parser)

    repetition.endLine = parser.line
    repetition.endColumn = parser.column
    parseLiteral(repetition, '*', parser)

    return repetition

def parseException(parent: nodes.Node, parser: ParserState) -> nodes.Exception:
    exception = nodes.Exception()
    parent.addChild(exception, parser.pt)

    exception.startLine = parser.line
    exception.startColumn = parser.column

    while True:
        if parser.c.isspace():
            parseSpace(exception, parser)
        elif parser.c.isalpha() or parser.c in PRIMARY_START_SYMBOLS:
            exception.primary = parsePrimary(exception, parser)
        else:
            #Let the parent handle it
            break

    if exception.primary == None:
        exception.primary = parseEmptyString(exception, parser)

    exception.endLine = exception.children[-1].endLine
    exception.endColumn = exception.children[-1].endColumn
    return exception

def parsePrimary(parent: nodes.Node, parser: ParserState) -> nodes.Primary:
    if parser.c.isalpha() or parser.c in PRIMARY_START_SYMBOLS:

        if parser.c.isalpha():
            return parseIdentifier(parent, parser)
        elif parser.c in TERMINAL_START_SYMBOLS:
            return parseTerminal(parent, parser)
        elif parser.c == '{':
            return parseRepeat(parent, None, parser)
        elif parser.c == '[':
            return parseOption(parent, None, parser)
        elif parser.c == '(':
            lit = nodes.Literal()

            lit.startLine = parser.line
            lit.startColumn = parser.column
            lit.endLine = parser.line
            lit.endColumn = parser.column

            lit.data += '('

            parser.readNoEOF(1, 'reading primary')

            if parser.c in ['/', ':']:
                lit.data += parser.c
                lit.endColumn = parser.column

                oc = parser.c
                parser.read(1)

                if oc == '/':
                    return parseRepeat(parent, lit, parser)
                elif oc == ':':
                    return parseOption(parent, lit, parser)
                else:
                    raise ParsingError('Bug! Unreachable', parser)
            else:
                return parseGroup(parent, lit, parser)
        elif parser.c == '?':
            return parseSpecial(parent, parser)
        else:
            raise ParsingError('Bug! Unreachable', parser)
    else:
        raise UnexpectedCharacterError(parser, f'expected a letter or one of {PRIMARY_START_SYMBOLS}')
def parseEmptyTerm(parent: nodes.Node, parser: ParserState) -> nodes.Term:
    term = nodes.Term()
    parent.addChild(term, parser.pt)

    term.startLine = parser.line
    term.endLine = parser.line
    term.startColumn = parser.column
    term.endColumn = parser.column - 1

    term.primary = parseEmptyString(term, parser)

    return term

def parseTerminal(parent: nodes.Node, parser: ParserState) -> nodes.Terminal:
    if not parser.c in TERMINAL_START_SYMBOLS:
        raise UnexpectedCharacterError(parser,
                                       f'one of '
                                       f'{TERMINAL_START_SYMBOLS}'
                                       )

    terminal = nodes.Terminal()
    parent.addChild(terminal, parser.pt)

    terminal.startLine = parser.line
    terminal.startColumn = parser.column

    lit = parseLiteral(terminal, parser.c, parser)

    text = nodes.Text()
    terminal.addChild(text, parser.pt)

    text.startLine = parser.line
    text.startColumn = parser.column

    while parser.c != lit.data:
        text.data += parser.c
        parser.readNoEOF(1, 'reading terminal')

    text.endLine = parser.line
    text.endColumn = parser.column - 1

    terminal.endLine = parser.line
    terminal.endColumn = parser.column

    parseLiteral(terminal, lit.data, parser)

    return terminal

def parseRepeat(parent: nodes.Node, lit: nodes.Literal | None,
                parser: ParserState) -> nodes.Repeat:
    repeat = nodes.Repeat()
    parent.addChild(repeat, parser.pt)

    repeat.startLine = parser.line
    repeat.startColumn = parser.column

    if lit is None:
        parseLiteral(repeat, ['{', '(/'], parser)
    else:
        repeat.addChild(lit, parser.pt)
        repeat.startLine = lit.startLine
        repeat.startColumn = lit.startColumn

    if parser.c.isspace():
        parseSpace(repeat, parser)

    defList, lit = parseDefinitionList(repeat, parser)

    if lit is None:
        repeat.endLine = parser.line
        repeat.endColumn = parser.column
        #No need to check for '/)' since the definition list would have parsed
        #it if it were there.
        parseLiteral(repeat, '}', parser)
    else:
        repeat.endLine = lit.endLine
        repeat.endColumn = lit.endColumn
        repeat.addChild(lit, parser.pt)

    return repeat

def parseOption(parent: nodes.Node, lit: nodes.Literal | None,
                parser: ParserState) -> nodes.Option:
    option = nodes.Option()
    parent.addChild(option, parser.pt)

    option.startLine = parser.line
    option.startColumn = parser.column

    if lit is None:
        parseLiteral(option, ['(:', '['], parser)
    else:
        option.addChild(lit, parser.pt)
        option.startLine = lit.startLine
        option.startColumn = lit.startColumn

    if parser.c.isspace():
        parseSpace(option, parser)

    defList, otherLit = parseDefinitionList(option, parser)

    if otherLit is not None:
        raise UnexpectedLiteralError(otherLit, parser)

    option.endLine = parser.line
    option.endColumn = parser.column

    lit = parseLiteral(option, [']', ':)'], parser)

    if lit.data == ':)':
        option.endColumn += 1

    return option

def parseGroup(parent: nodes.Node, lit: nodes.Literal| None,
               parser: ParserState) -> nodes.Group:
    group = nodes.Group()
    parent.addChild(group, parser.pt)

    group.startLine = parser.line
    group.startColumn = parser.column

    if lit is None:
        parseLiteral(group, '(', parser)
    else:
        group.addChild(lit, parser.pt)
        group.startLine = lit.startLine
        group.startColumn = lit.startColumn

    if parser.c.isspace():
        parseSpace(group, parser)

    defList, otherLit = parseDefinitionList(group, parser)

    if otherLit is not None:
        raise UnexpectedLiteralError(otherLit, parser)

    group.endLine = parser.line
    group.endColumn = parser.column

    parseLiteral(group, ')', parser)

    return group

def parseSpecial(parent: nodes.Node, parser: ParserState) -> nodes.Special:
    special = nodes.Special()
    parent.addChild(special, parser.pt)

    special.startLine = parser.line
    special.startColumn = parser.column

    parseLiteral(special, '?', parser)

    text = nodes.Text()
    text.startLine = parser.line
    text.startColumn = parser.column
    text.endLine = parser.line
    text.endColumn = parser.column - 1
    special.addChild(text, parser.pt)
    while parser.c != '?':
        text.data += parser.c
        text.endLine = parser.line
        text.endColumn = parser.column
        parser.readNoEOF(1, 'reading special')

    special.endLine = parser.line
    special.endColumn = parser.column

    parseLiteral(special, '?', parser)

    return special

def parseEmptyString(parent: nodes.Node, parser: ParserState) -> nodes.EmptyString:
    emptyString = nodes.EmptyString()
    parent.addChild(emptyString, parser.pt)

    emptyString.startLine = parser.line
    emptyString.startColumn = parser.column
    emptyString.endLine = parser.line
    emptyString.endColumn = parser.column - 1

    return emptyString


class ParsingError(EBNFError):
    def __init__(self, message, parser: ParserState):
        super().__init__(message)
        self.parser = parser

class EOFError(ParsingError):
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
    def __init__(self, parser: ParserState):
        super().__init__(f'Expected a space character at '
                         f'{parser.line},{parser.column}, but found '
                         f'`{parser.c}`', parser
                         )

class NoLiteralError(ParsingError):
    def __init__(self, parser: ParserState, literals: list | str, read: str):
        super().__init__(f'Could not find match {literals} at '
                         f'{parser.line},{parser.column}', parser
                         )
        self.literals = literals
        self.read = read

class UndelimitedTermError(ParsingError):
    def __init__(self, term: nodes.Term, parser: ParserState):
        super().__init__(f'Start of another term at '
                         f'{parser.line},{parser.column} before previous term '
                         f'at {term.startLine},{term.startColumn} terminated',
                         parser
                         )

class MultipleTermRepetitions(ParsingError):
    def __init__(self, term: nodes.Term, parser: ParserState):
        super().__init__(f'Term can only have one repetition, another defined '
                         f'at {parser.line},{parser.column}, last one defined '
                         f'at {term.repetition.startLine},'
                         f'{term.repetition.startColumn}',
                         parser
                         )

class MultipleTermExceptions(ParsingError):
    def __init__(self, term: nodes.Term, parser: ParserState):
        super().__init__(f'Unexpected `-`, term started at '
                         f'{term.startLine},{term.startColumn} already has an '
                         f'exception defined at '
                         f'{term.exception.startLine},'
                         f'{term.exception.startColumn}',
                         parser
                         )

class MultipleTermPrimariesError(ParsingError):
    def __init__(self, term: nodes.Term, parser: ParserState):
        super().__init__(f'Term started at {term.startLine},{term.startColumn} '
                         f'can only have one primary, however another defined '
                         f'at {parser.line},{parser.column}',
                         parser
                         )

class UnexpectedLiteralError(ParsingError):
    def __init__(self, lit: nodes.Literal, parser: ParserState):
            super().__init__(f'Did not expect literal `{lit.data}` at '
                             f'{lit.startLine},{lit.startColumn}', parser
                             )
