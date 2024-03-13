# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

import pytest
import glob

pytestmark = pytest.mark.parametrize("ebnf_path", glob.glob("tests/resources/valid/*"))

def test_example(ebnf_path):

    from parse_ebnf import PT

    #Your EBNF file goes here
    ebnf = open(ebnf_path, 'r')

    pt = PT()

    try:
        #Will raise SyntaxError on error with an error message describing what went wrong
        pt.parse(ebnf.read) #You need to pass in a function that returns n characters where n is given as the first parameter.
    finally:
        #Even after an error a partial tree will be generated.
        #str gives a text version of the parse tree(meant for debugging), while repr gives the text that it was produced from.
        print(str(pt))

    print(f'Parsed the file creating a tree with {pt.count} nodes, height of {pt.height}. Each node has at MOST {pt.maxDegree} children.')

    def DepthFirst(node, func):
        func(node)
        for child in node.children:
            DepthFirst(child, func)

    #This will visit each node in the parse tree and print the line where its text begins
    DepthFirst(pt.root, lambda node: print(node.startLine))

    from parse_ebnf.nodes import Comment

    #Finds each comment in the file and prints its text content
    for child in pt.root.children:
        if isinstance(child, Comment):
            print(child.data)

