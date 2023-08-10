# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

import pytest
import glob

pytestmark = pytest.mark.parametrize("ebnf_path", glob.glob("tests/resources/valid/*"))

def test_example(ebnf_path):

    from parse_ebnf import AST

    #Your EBNF file goes here
    ebnf = open(ebnf_path, 'r')

    ast = AST()

    try:
        #Will raise SyntaxError on error with an error message describing what went wrong
        ast.parse(ebnf.read) #You need to pass in a function that returns n characters where n is given as the first parameter.
    finally:
        #Even after an error a partial tree will be generated.
        #str gives a text version of the parse tree(meant for debugging), while repr gives the text that it was produced from.
        print(str(ast))

    print(f'Parsed the file creating a tree with {ast.count} nodes, height of {ast.height}. Each node has at MOST {ast.maxDegree} children.')

    def DepthFirst(node, func):
        func(node)
        for child in node.children:
            DepthFirst(child, func)

    #This will visit each node in the parse tree and print the line where its text begins
    DepthFirst(ast.root, lambda node: print(node.startLine))

    from parse_ebnf import ASTCommentNode

    #Finds each comment in the file and prints its text content
    for child in ast.root.children:
        if isinstance(child, ASTCommentNode):
            print(child.data)

