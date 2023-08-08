# Parse EBNF

[![PyPI - Version](https://img.shields.io/pypi/v/parse-ebnf.svg)](https://pypi.org/project/parse-ebnf)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/parse-ebnf.svg)](https://pypi.org/project/parse-ebnf)

-----

**Table of Contents**

- [Introduction](#introduction)
- [Installation](#installation)
- [Quick start](#quickstart)
- [Documentation](#documentation)
- [License](#license)

## Introduction

A simple and hacky parser for EBNF as defined by ISO. Give it an EBNF string and
it'll generate a **parse tree**. Note that this package does not parse the
described grammar.

## Installation

```console
pip install parse-ebnf
```
## Quick start

```python
from parse_ebnf import AST

#Your EBNF file goes here
ebnf = open('grammar.ebnf', 'r')

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
```

## Documentation

Check the [github page](https://chaosinventor.github.io/parse-ebnf/) that
holds the documentation.

## License

`parse-ebnf` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

