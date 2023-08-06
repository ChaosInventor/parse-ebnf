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
.. |AST| replace:: :py:class:`parse_ebnf.AST`
.. |ASTNode| replace:: :py:class:`parse_ebnf.ASTNode`
.. |ASTRootNode| replace:: :py:class:`parse_ebnf.ASTRootNode`
.. |ASTTextNode| replace:: :py:class:`parse_ebnf.ASTTextNode`
.. |ASTCommentNode| replace:: :py:class:`parse_ebnf.ASTCommentNode`
.. |ASTSpaceNode| replace:: :py:class:`parse_ebnf.ASTSpaceNode`
.. |ASTIdentifierNode| replace:: :py:class:`parse_ebnf.ASTIdentifierNode`
.. |ASTLiteralNode| replace:: :py:class:`parse_ebnf.ASTLiteralNode`
.. |ASTProductNode| replace:: :py:class:`parse_ebnf.ASTProductNode`
.. |ASTDefinitionListNode| replace:: :py:class:`parse_ebnf.ASTDefinitionListNode`
.. |ASTDefinitionNode| replace:: :py:class:`parse_ebnf.ASTDefinitionNode`
.. |ASTTermNode| replace:: :py:class:`parse_ebnf.ASTTermNode`
.. |ASTExceptionNode| replace:: :py:class:`parse_ebnf.ASTExceptionNode`
.. |ASTRepetitionNode| replace:: :py:class:`parse_ebnf.ASTRepetitionNode`
.. |ASTTerminalNode| replace:: :py:class:`parse_ebnf.ASTTerminalNode`
.. |ASTRepeatNode| replace:: :py:class:`parse_ebnf.ASTRepeatNode`
.. |ASTOptionNode| replace:: :py:class:`parse_ebnf.ASTOptionNode`
.. |ASTGroupNode| replace:: :py:class:`parse_ebnf.ASTGroupNode`
.. |ASTSpecialNode| replace:: :py:class:`parse_ebnf.ASTSpecialNode`
.. |ASTEmptyNode| replace:: :py:class:`parse_ebnf.ASTEmptyNode`
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
