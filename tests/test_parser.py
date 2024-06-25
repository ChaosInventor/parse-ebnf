# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

import pytest
import glob
import inspect
import io
from parse_ebnf import PT, parsing, EBNFError
from parse_ebnf.nodes import *

pytestmark = pytest.mark.parametrize(
        "ebnf_path",
        [p for ps in [glob.glob("tests/resources/valid/*"),
                      glob.glob("tests/resources/invalid/*")
                     ] for p in ps])

@pytest.fixture
def ebnf(ebnf_path):
    ebnf = open(ebnf_path, 'r')

    pt = PT()
    partial = False

    if "/valid/" in ebnf_path: pt = parsing.parsePT(ebnf.read)
    else:
        with pytest.raises(EBNFError) as error:
            pt = parsing.parsePT(ebnf.read)
            #In case a syntax error did not occur, print the PT for inspection
            print(str(pt))
        pt = error.value.parser.pt
        partial = True

    yield pt, ebnf, ebnf_path, partial

    ebnf.close()

def test_pt_yield(ebnf):
    pt, file, path, partial = ebnf

    buffer = io.StringIO()
    pt.unparse(buffer.write)

    file.seek(0)

    if partial: assert file.read().startswith(buffer.getvalue())
    else: assert file.read() == buffer.getvalue()

    buffer.close()

def cleanArgs(*args):
    ret = []
    for arg in args:
        if inspect.isclass(arg):
            def i(t):
                def instance(node, index):
                    assert index < len(node.children), "Ran out of children nodes for predicate"
                    assert isinstance(node.children[index], t)
                    return index + 1

                return instance
            ret.append(i(arg))
        else: ret.append(arg)
    return ret
def literal(s):
    def l(node, index):
        assert index < len(node.children), "Ran out of children nodes for literal"

        assert isinstance(node.children[index], Literal)
        if isinstance(s, str):
            assert node.children[index].data == s
        else:
            for string in s:
                if node.children[index].data == string: return index + 1
            assert False, "Literal does not contain any of the specified strings"
        return index + 1

    return l
def predicate(*args):
    cleaned = cleanArgs(*args)

    def p(node, index):
        i = index
        for arg in cleaned:
            i = arg(node, i)

        return i

    return p
def either(*args):
    cleaned = cleanArgs(*args)

    def e(node, index):
        for arg in cleaned:
            try:
                return arg(node, index)
            except AssertionError: continue
        assert False, "Node does not comply with any of the given predicates"

    return e
def zero_or_more(*args):
    cleaned = cleanArgs(*args)

    def a(node, index):
        i = index
        p = predicate(*args)
        try:
            i = p(node, i)
        except AssertionError: return i
        while i >= 0 and i < len(node.children):
            try:
                i = p(node, i)
            except AssertionError: break
        return i

    return a
def maybe(*args):
    def m(node, index):
        if index >= len(node.children): return index
        p = predicate(*args)
        try:
            return p(node, index)
        except AssertionError: return index

    return m
def check_node_children(node, *args):
    i = 0
    p = predicate(*args)
    newIndex = p(node, i)
    assert newIndex >= 0, "Error while checking node children"
    assert newIndex == len(node.children), "Did not check all node children, too many"
def parent_is_either(node, *args):
    ret = False
    for arg in args:
        if isinstance(node.parent, arg): ret = True

    return ret
def check_node_structure(node, depth=0):
    assert isinstance(node, Node)
    assert node.depth == depth

    for child in node:
        assert child.parent == node

    # In case the iterator for nodes isn't implemented properly
    for child in node:
        assert child.parent == node

    if isinstance(node, Leaf):
        assert isinstance(node.data, str)
        assert len(node.children) == 0

    if not isinstance(node, Root):
        assert node.parent is not None
        assert isinstance(node.parent, Node)

    #TODO: Perfect tree by not allowing the last or first node to ever be a
    #space, with the exception of the root
    if isinstance(node, Root):
        assert node.parent is None

        check_node_children(node, zero_or_more(either(Comment, Product, Space)))
    elif isinstance(node, Comment):
        assert parent_is_either(node, Root, Comment)

        check_node_children(node, literal("(*"), zero_or_more(either(Comment, Text)), literal("*)"))
    elif isinstance(node, Product):
        assert parent_is_either(node, Root)

        check_node_children(node, Identifier, maybe(Space), literal("="), maybe(Space), DefinitionList, maybe(Space), literal([";", "."]))
    elif isinstance(node, Space):
        assert parent_is_either(node,
            Root, Product, DefinitionList, Definition, Term, Repetition,
            Exception, Repeat, Option, Group
        )

        for c in node.data:
            assert c.isspace()
    elif isinstance(node, Literal):
        assert parent_is_either(node,
            Comment, Product, DefinitionList, Definition, Term, Repetition,
            Terminal, Repeat, Option, Group, Special
        )

        assert node.data != ''
    elif isinstance(node, Identifier):
        assert parent_is_either(node, Product, Definition, Term, Exception)

        assert node.data == node.data.rstrip()
        assert node.data[0].isalpha()
        for c in node.data:
            assert c.isalpha() or c.isnumeric() or c.isspace()
    elif isinstance(node, DefinitionList):
        assert parent_is_either(node, Product, Repeat, Option, Group)

        check_node_children(node,
            zero_or_more(maybe(Space), Definition, maybe(Space),
            literal(["|", "/", "!"])), maybe(Space), maybe(Definition),
            maybe(Space)
        )
    elif isinstance(node, Definition):
        assert parent_is_either(node, DefinitionList)

        check_node_children(node,
            maybe(Space), zero_or_more(Term, maybe(Space),
            literal(","), maybe(Space)), maybe(Term,
            maybe(literal(","))), maybe(Space)
        )
    elif isinstance(node, Term):
        assert parent_is_either(node, Definition)

        check_node_children(node,
            maybe(Space), maybe(Repetition), maybe(Space), Primary,
            maybe(Space), maybe(literal("-"), Exception)
        )
    elif isinstance(node, Repetition):
        assert parent_is_either(node, Term)

        check_node_children(node, maybe(Space), literal("*"), maybe(Space))
    elif isinstance(node, Exception):
        assert parent_is_either(node, Term)

        check_node_children(node, maybe(Space), Primary, maybe(Space))
    elif isinstance(node, Terminal):
        assert parent_is_either(node, Term, Exception)

        check_node_children(node, literal(['"', "'", '`']), Text, literal(['"', "'", '`']))
        assert node.children[0].data == node.children[2].data
    elif isinstance(node, Repeat):
        assert parent_is_either(node, Term, Exception)

        check_node_children(node, literal(["{", "(/"]), maybe(Space), DefinitionList, literal(["}", "/)"]))
    elif isinstance(node, Option):
        assert parent_is_either(node, Term, Exception)

        check_node_children(node, literal(["[", "(:"]), maybe(Space), DefinitionList, literal(["]", ":)"]))
    elif isinstance(node, Group):
        assert parent_is_either(node, Term, Exception)

        check_node_children(node, literal("("), maybe(Space), DefinitionList, literal(")"))
    elif isinstance(node, Special):
        assert parent_is_either(node, Term, Exception)

        check_node_children(node, literal("?"), Text, literal("?"))
    elif isinstance(node, EmptyString):
        assert parent_is_either(node, Term, Exception)

        assert node.data == ''
    elif isinstance(node, Text):
        assert parent_is_either(node, Comment, Terminal, Special)
    else:
        raise BaseException("Unknown node type")

    for child in node:
        check_node_structure(child, depth+1)
def test_pt_structure(ebnf):
    pt, file, path, partial = ebnf

    assert isinstance(pt.root, Root)

    check_node_structure(pt.root)

def count_node(node, depth=0):
    assert isinstance(node, Node)

    count = 1
    height = depth
    maxDegree = len(node.children)

    for child in node:
        c, h, d = count_node(child, depth+1)
        count += c
        height = h if h > height else height
        maxDegree = d if d > maxDegree else maxDegree

    return count, height, maxDegree
def test_pt(ebnf):
    pt, file, path, partial = ebnf

    count, height, maxDegree = count_node(pt.root)

    assert count == pt.count
    assert height == pt.height
    assert maxDegree == pt.maxDegree

def check_node_coordinates(node, ebnf):
    assert isinstance(node, Node)

    assert node.startLine >= 0
    assert node.endLine >= 0
    assert node.startColumn >= 0
    assert node.startLine <= node.endLine

    if node.startLine == node.endLine:
        if node.startColumn > node.endColumn:
            assert str(node) == ''
            for child in node:
                check_node_coordinates(child, ebnf)
            return
        else:
            assert node.endColumn >= 0

    ebnf.seek(0)
    line = None
    for i in range(node.startLine):
        line = ebnf.readline()

    text = ''
    if node.startColumn == 0:
        text += '\n'
    if node.startLine == node.endLine:
        text += line[node.startColumn - 1 if node.startColumn > 0 else 0 : node.endColumn]
    else:
        text += line[node.startColumn - 1:] if node.startColumn > 0 else line
        for i in range(node.endLine - node.startLine):
            line = ebnf.readline()
            if node.startLine + i + 1 == node.endLine: text += line[:node.endColumn]
            else: text += line

    assert text == str(node)

    for child in node:
        check_node_coordinates(child, ebnf)
def test_pt_coordinates(ebnf):
    pt, file, path, partial = ebnf

    check_node_coordinates(pt.root, file)

