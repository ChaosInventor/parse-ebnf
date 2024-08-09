parse-ebnf's documentation
==========================

Introduction
------------

parse-ebnf is a parser for EBNF, Extended Backus-Naur Form. Give it an EBNF
input and it will generate a parse tree.

.. note:: **This package does not generate a parser for the described grammar.**

Installation
------------

.. code-block:: shell

    pip install parse-ebnf

.. _example:
.. index:: example

Quick start
-----------

.. code-block:: python

    from parse_ebnf import parse_file
    from parse_ebnf.parsing import ParsingError

    try:
        #Your EBNF file goes here.
        pt = parse_file(ebnf_path)
        partial = False
    except ParsingError as e:
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
    #text begins.
    DepthFirst(pt.root, partial, lambda node: print(node.startLine))

    from parse_ebnf.nodes import Comment

    #Finds each comment in the file and prints its text content.
    for child in pt.root.children:
        if isinstance(child, Comment):
            #A tree being partial means that its root is partial.
            if partial and child is pt.root.children[-1]: continue
            print(str(child))

Reference
=========

.. toctree::
   :maxdepth: 1

    Parsing <parsing.rst>
    Parse tree <tree.rst>
    Errors <errors.rst>
    Testing <testing.rst>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

