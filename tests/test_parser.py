# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

import glob
import io
import itertools
from importlib import import_module

import pytest

from parse_ebnf import PT, EBNFError, parse_file, parse_from_function, parse_string
from parse_ebnf.nodes import *
from parse_ebnf.parsing import parse_pt
from tests.tree_structure import check_node_children, parent_is_either


def parse_with_parse_pt(ebnf_path):
    with open(ebnf_path) as ebnf:
        return parse_pt(ebnf.read)
def parse_with_parse_string(ebnf_path):
    with open(ebnf_path) as ebnf:
        return parse_string(ebnf.read())
def parse_with_parse_from_function(ebnf_path):
    with open(ebnf_path) as ebnf:
        return parse_from_function(ebnf.read)

pytestmark = pytest.mark.parametrize(
        "ebnf_path,parse_function",
        [*itertools.product(
            (p for ps in [glob.glob("tests/resources/valid/*"),
                          glob.glob("tests/resources/invalid/*")
                          ] for p in ps),
            (parse_with_parse_pt, parse_file, parse_with_parse_string,
             parse_with_parse_from_function
             )
            )]
        )

@pytest.fixture
def ebnf(ebnf_path, parse_function):
    ebnf = open(ebnf_path)

    pt = PT()
    partial = False

    if "/valid/" in ebnf_path: pt = parse_function(ebnf_path)
    else:
        with pytest.raises(EBNFError) as error:
            pt = parse_function(ebnf_path)
            #In case a syntax error did not occur, print the PT for inspection
            print(repr(pt)) #no cov
            pytest.xfail("Invalid example did not raise exception") #no cov
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

    if not partial:
        if isinstance(node, Terminal):
            assert node.children[0].data == node.children[2].data
        if isinstance(node, Product):
            for child in node:
                if isinstance(child, Identifier): assert node.lhs is child
                elif isinstance(child, DefinitionList): assert node.rhs is child
        if isinstance(node, Term):
            repetition = None
            primary = None
            exception = None
            for child in node:
                if isinstance(child, Repetition):
                    assert repetition is None
                    repetition = child
                elif isinstance(child, Primary):
                    assert primary is None
                    primary = child
                elif isinstance(child, Exception):
                    assert exception is None
                    exception = child

            assert node.repetition is repetition
            assert node.primary is primary
            assert node.exception is exception
        if isinstance(node, Exception):
            primary = None
            for child in node:
                if isinstance(child, Primary):
                    assert primary is None
                    primary = child

            assert node.primary is primary
        if isinstance(node, (Group, Option, Repeat)):
            assert node.children[0] is node.lit

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

def test_pt_node_write(ebnf):
    pt, file, path, partial = ebnf

    ptBuffer = io.StringIO()
    nodeBuffer = io.StringIO()

    pt.write(ptBuffer.write)
    pt.root.write(nodeBuffer.write)

    ptBuffer.seek(0)
    nodeBuffer.seek(0)

    ptBuffer.readline()
    assert ptBuffer.read() == nodeBuffer.read()

def test_pt_node_unparse(ebnf):
    pt, file, path, partial = ebnf

    ptBuffer = io.StringIO()
    nodeBuffer = io.StringIO()

    pt.unparse(ptBuffer.write)
    pt.root.unparse(nodeBuffer.write)

    ptBuffer.seek(0)
    nodeBuffer.seek(0)

    assert ptBuffer.read() == nodeBuffer.read()

