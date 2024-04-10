# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

import pytest
import glob
from parse_ebnf import PT, parsing, EBNFError
from parse_ebnf.nodes import Root

pytestmark = pytest.mark.parametrize("ebnf_path", glob.glob("tests/resources/valid/*"))

def test_parser(tmp_path, ebnf_path):
    ebnf = open(ebnf_path, 'r')

    pt = PT()
    try:
        pt = parsing.parsePT(ebnf.read)
    except EBNFError as e:
        print(str(e.parser.pt))
        raise e

    tmpFile = open(tmp_path / 'tmp', 'w+')
    pt.unparse(tmpFile.write)

    ebnf.seek(0)
    tmpFile.seek(0)

    assert ebnf.read() == tmpFile.read()

    tmpFile.close()
    ebnf.close()

def test_pt(ebnf_path):
    ebnf = open(ebnf_path, 'r')

    pt = PT()
    try:
        pt = parsing.parsePT(ebnf.read)
    except EBNFError as e:
        print(str(e.parser.pt))
        raise e

    assert isinstance(pt.root, Root)

    class NodeCounter:
        def __init__(self, root):
            self.root = root
            self.height = 0
            self.degree = 0
            self.count = 0
            self.countNodes(self.root)
        def countNodes(self, node, depth=0):
            self.height = depth if depth > self.height else self.height
            self.degree = len(node.children) if len(node.children) > self.degree else self.degree
            self.count += 1
            for child in node:
                self.countNodes(child, depth+1)

    counter = NodeCounter(pt.root)

    assert counter.height == pt.height
    assert counter.degree == pt.maxDegree
    assert counter.count == pt.count

    ebnf.close()

def test_pt_coordinates(ebnf_path):
    ebnf = open(ebnf_path, 'r')

    pt = PT()
    try:
        pt = parsing.parsePT(ebnf.read)
    except:
        print(str(pt))

    class CoordinateChecker:
        def __init__(self, root, ebnf):
            self.root = root
            self.ebnf = ebnf
            self.check(self.root)
        def check(self, node):
            print(str(node))
            assert node.startLine >= 0
            assert node.endLine >= 0
            assert node.startColumn >= 0

            assert node.startLine <= node.endLine
            if node.startLine == node.endLine:
                if node.startColumn > node.endColumn:
                    assert repr(node) == ''
                    for child in node:
                        self.check(child)
                    return
                else: assert node.endColumn >= 0

            self.ebnf.seek(0)

            line = None
            for i in range(node.startLine):
                line = ebnf.readline()

            text = ''
            if node.startColumn == 0:
                text += '\n'
            if node.startLine == node.endLine:
                text += line[node.startColumn - 1 if node.startColumn > 0 else 0:node.endColumn]
            else:
                text += line[node.startColumn - 1:] if node.startColumn > 0 else line
                for i in range(node.endLine - node.startLine):
                    line = ebnf.readline()
                    if node.startLine + i + 1 == node.endLine: text += line[:node.endColumn]
                    else: text += line

            assert text == repr(node)

            for child in node:
                self.check(child)

    checker = CoordinateChecker(pt.root, ebnf)

    ebnf.close()

