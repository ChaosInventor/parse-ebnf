# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

import pytest
import glob
from parse_ebnf import PT, parsing, EBNFError
from parse_ebnf.nodes import Root

pytestmark = pytest.mark.parametrize("ebnf_path", glob.glob("tests/resources/valid/*"))

@pytest.fixture
def ebnf(ebnf_path):
    ebnf = open(ebnf_path, 'r')

    pt = PT()
    try:
        pt = parsing.parsePT(ebnf.read)
    except EBNFError as e:
        print(str(e.parser.pt))
        raise e

    yield pt, ebnf, ebnf_path

    ebnf.close()

def test_parser(tmp_path, ebnf):
    pt, file, path = ebnf

    tmpFile = open(tmp_path/'tmp', 'w+')
    pt.unparse(tmpFile.write)

    file.seek(0)
    tmpFile.seek(0)

    assert file.read() == tmpFile.read()

    tmpFile.close()

def count_node(node, depth=0):
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
    pt, file, path = ebnf

    assert isinstance(pt.root, Root)

    count, height, maxDegree = count_node(pt.root)

    assert count == pt.count
    assert height == pt.height
    assert maxDegree == pt.maxDegree

def check_node_coordinates(node, ebnf):
    print(str(node))

    assert node.startLine >= 0
    assert node.endLine >= 0
    assert node.startColumn >= 0
    assert node.startLine <= node.endLine

    if node.startLine == node.endLine:
        if node.startColumn > node.endColumn:
            assert repr(node) == ''
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

    assert text == repr(node)

    for child in node:
        check_node_coordinates(child, ebnf)
def test_pt_coordinates(ebnf):
    pt, file, path = ebnf

    check_node_coordinates(pt.root, file)

