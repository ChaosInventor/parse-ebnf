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
from parse_ebnf import parse_file, EBNFError

try:
    #Your EBNF file goes here
    pt = parse_file(ebnf_path)
    partial = False
except EBNFError as e:
    #If an exception occurs, a partial tree is generated. See the docs for
    #details.
    pt = e.parser.pt
    partial = True

#Prints the text that the tree was parsed from.
print(str(pt))
#Prints a debug view of the tree.
print(repr(pt))

print(f'Parsing the file created a tree with {pt.count} nodes.')
print(f'The tree has a height of {pt.height}.')
print(f'Each node in the tree has at MOST {pt.maxDegree} children.')

def DepthFirst(node, partial, func):
    #Partial nodes are in a mostly undefined state.
    if not partial: func(node)
    for child in node.children:
        #If a node is partial, then its last child is partial. All other
        #children are not partial.
        if partial and child is node.children[-1]:
            DepthFirst(child, True, func)
        else:
            DepthFirst(child, False, func)

#This will visit each node in the parse tree and print the line where its
#text begins
DepthFirst(pt.root, partial, lambda node: print(node.startLine))

from parse_ebnf.nodes import Comment

#Finds each comment in the file and prints its text content
for child in pt.root.children:
    if isinstance(child, Comment):
        #A tree being partial means that its root is partial.
        if partial and child is pt.root.children[-1]: continue
        print(str(child))
```

## Documentation

Check the [github page](https://chaosinventor.github.io/parse-ebnf/) that
holds the documentation.

## License

`parse-ebnf` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

