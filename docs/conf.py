# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys, os

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'parse-ebnf'
copyright = '2023, ChaosInventor'
author = 'ChaosInventor'
release = '1.0'

sys.path.append('..')

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

rst_prolog = """
.. |AST| replace:: :py:class:`AST <parse_ebnf.AST>`
.. |ASTNode| replace:: :py:class:`ASTNode <parse_ebnf.ASTNode>`
.. |ASTRootNode| replace:: :py:class:`ASTRootNode <parse_ebnf.ASTRootNode>`
.. |ASTTextNode| replace:: :py:class:`ASTTextNode <parse_ebnf.ASTTextNode>`
.. |ASTCommentNode| replace:: :py:class:`ASTCommentNode <parse_ebnf.ASTCommentNode>`
.. |ASTSpaceNode| replace:: :py:class:`ASTSpaceNode <parse_ebnf.ASTSpaceNode>`
.. |ASTIdentifierNode| replace:: :py:class:`ASTIdentifierNode <parse_ebnf.ASTIdentifierNode>`
.. |ASTLiteralNode| replace:: :py:class:`ASTLiteralNode <parse_ebnf.ASTLiteralNode>`
.. |ASTProductNode| replace:: :py:class:`ASTProductNode <parse_ebnf.ASTProductNode>`
.. |ASTDefinitionListNode| replace:: :py:class:`ASTDefinitionListNode <parse_ebnf.ASTDefinitionListNode>`
.. |ASTDefinitionNode| replace:: :py:class:`ASTDefinitionNode <parse_ebnf.ASTDefinitionNode>`
.. |ASTTermNode| replace:: :py:class:`ASTTermNode <parse_ebnf.ASTTermNode>`
.. |ASTExceptionNode| replace:: :py:class:`ASTExceptionNode <parse_ebnf.ASTExceptionNode>`
.. |ASTRepetitionNode| replace:: :py:class:`ASTRepetitionNode <parse_ebnf.ASTRepetitionNode>`
.. |ASTTerminalNode| replace:: :py:class:`ASTTerminalNode <parse_ebnf.ASTTerminalNode>`
.. |ASTRepeatNode| replace:: :py:class:`ASTRepeatNode <parse_ebnf.ASTRepeatNode>`
.. |ASTOptionNode| replace:: :py:class:`ASTOptionNode <parse_ebnf.ASTOptionNode>`
.. |ASTGroupNode| replace:: :py:class:`ASTGroupNode <parse_ebnf.ASTGroupNode>`
.. |ASTSpecialNode| replace:: :py:class:`ASTSpecialNode <parse_ebnf.ASTSpecialNode>`
.. |ASTEmptyNode| replace:: :py:class:`ASTEmptyNode <parse_ebnf.ASTEmptyNode>`
.. |ASTEmptyTerm| replace:: :py:class:`ASTEmptyTerm <parse_ebnf.ASTEmptyTerm>`

.. |or| replace:: :ref:`| <groups>`
.. |maybe| replace:: :ref:`? <optional>`
.. |any| replace:: :ref:`* <any>`
.. |more| replace:: :ref:`+ <more>`
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
