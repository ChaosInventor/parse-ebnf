# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

import pytest
import glob
import io
from parse_ebnf import PT, parsing, EBNFError
from parse_ebnf.nodes import *
from importlib import import_module
from tests.tree_structure import check_node_children, parent_is_either

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

    if "/valid/" in ebnf_path: pt = parsing.parse_pt(ebnf.read)
    else:
        with pytest.raises(EBNFError) as error:
            pt = parsing.parse_pt(ebnf.read)
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

def check_node_structure(node, depth, partial):
    assert isinstance(node, Node)
    assert node.depth == depth

    for child in node:
        assert child.parent == node

    # In case the iterator for nodes isn't implemented properly
    for child in node:
        assert child.parent == node


    if not isinstance(node, Root):
        assert node.parent is not None
        assert isinstance(node.parent, Node)

    mod = import_module(f'tests.tree_structure.{type(node).__name__}')

    if isinstance(node, Root):
        assert node.parent is None
    else:
        assert parent_is_either(node, *mod.parents)

    if isinstance(node, Leaf):
        assert isinstance(node.data, str)
        assert len(node.children) == 0

        if isinstance(node, Space):
            if not partial:
                for c in node.data:
                    assert c.isspace()
        elif isinstance(node, Literal):
            if not partial: assert node.data != ''
        elif isinstance(node, Identifier):
            if not partial:
                assert node.data == node.data.rstrip()
                assert node.data[0].isalpha()
                for c in node.data:
                    assert c.isalpha() or c.isnumeric() or c.isspace()
        elif isinstance(node, Number):
            if not partial:
                for c in node.data:
                    assert c.isnumeric()
        elif isinstance(node, EmptyString):
            if not partial: assert node.data == ''
    else:
        check_node_children(node, partial, *mod.children)

    if isinstance(node, Terminal):
        assert node.children[0].data == node.children[2].data

    for child in node:
        check_node_structure(child, depth+1, child is node.children[-1] and partial)
def test_pt_structure(ebnf):
    pt, file, path, partial = ebnf

    assert isinstance(pt.root, Root)

    check_node_structure(pt.root, 0, partial)

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
def test_pt_counters(ebnf):
    pt, file, path, partial = ebnf

    count, height, maxDegree = count_node(pt.root)

    assert count == pt.count
    assert height == pt.height
    assert maxDegree == pt.maxDegree

def check_node_coordinates(node, ebnf, partial):
    assert isinstance(node, Node)

    if not partial:
        assert node.startLine >= 0
        assert node.endLine >= 0
        assert node.startColumn >= 0
        assert node.startLine <= node.endLine

        if node.startLine == node.endLine:
            if node.startColumn > node.endColumn:
                assert str(node) == ''
                for child in node:
                    check_node_coordinates(child, ebnf, child is node.children[-1] and partial)
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
        check_node_coordinates(child, ebnf, child is node.children[-1] and partial)
def test_pt_coordinates(ebnf):
    pt, file, path, partial = ebnf

    check_node_coordinates(pt.root, file, partial)

