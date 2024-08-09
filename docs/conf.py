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
release = '2.0'

sys.path.append('..')

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

rst_prolog = """
.. |PT| replace:: :py:class:`PT <parse_ebnf.PT>`
.. |Node| replace:: :py:class:`Node <parse_ebnf.nodes.Node>`
.. |Leaf| replace:: :py:class:`Leaf <parse_ebnf.nodes.Leaf>`
.. |Primary| replace:: :py:class:`Primary <parse_ebnf.nodes.Primary>`
.. |Root| replace:: :py:class:`Root <parse_ebnf.nodes.Root>`
.. |Comment| replace:: :py:class:`Comment <parse_ebnf.nodes.Comment>`
.. |Product| replace:: :py:class:`Product <parse_ebnf.nodes.Product>`
.. |DefinitionList| replace:: :py:class:`DefinitionList <parse_ebnf.nodes.DefinitionList>`
.. |Definition| replace:: :py:class:`Definition <parse_ebnf.nodes.Definition>`
.. |Term| replace:: :py:class:`Term <parse_ebnf.nodes.Term>`
.. |Exception| replace:: :py:class:`Exception <parse_ebnf.nodes.Exception>`
.. |Repetition| replace:: :py:class:`Repetition <parse_ebnf.nodes.Repetition>`
.. |Terminal| replace:: :py:class:`Terminal <parse_ebnf.nodes.Terminal>`
.. |Repeat| replace:: :py:class:`Repeat <parse_ebnf.nodes.Repeat>`
.. |Option| replace:: :py:class:`Option <parse_ebnf.nodes.Option>`
.. |Group| replace:: :py:class:`Group <parse_ebnf.nodes.Group>`
.. |Special| replace:: :py:class:`Special <parse_ebnf.nodes.Special>`
.. |Identifier| replace:: :py:class:`Identifier <parse_ebnf.nodes.Identifier>`
.. |EmptyString| replace:: :py:class:`EmptyString <parse_ebnf.nodes.EmptyString>`
.. |Text| replace:: :py:class:`Text <parse_ebnf.nodes.Text>`
.. |Space| replace:: :py:class:`Space <parse_ebnf.nodes.Space>`
.. |Literal| replace:: :py:class:`Literal <parse_ebnf.nodes.Literal>`
.. |Number| replace:: :py:class:`Number <parse_ebnf.nodes.Number>`
.. |ParsingError| replace:: :py:class:`ParsingError <parse_ebnf.parsing.ParsingError>`
.. |EOFError| replace:: :py:class:`EOFError <parse_ebnf.parsing.EOFError>`
.. |UnexpectedCharacterError| replace:: :py:class:`UnexpectedCharacterError <parse_ebnf.parsing.UnexpectedCharacterError>`
.. |NoSpaceError| replace:: :py:class:`NoSpaceError <parse_ebnf.parsing.NoSpaceError>`
.. |NoLiteralError| replace:: :py:class:`NoLiteralError <parse_ebnf.parsing.NoLiteralError>`
.. |UndelimitedTermError| replace:: :py:class:`UndelimitedTermError <parse_ebnf.parsing.UndelimitedTermError>`
.. |MultipleTermRepetitions| replace:: :py:class:`MultipleTermRepetitions <parse_ebnf.parsing.MultipleTermRepetitions>`
.. |MultipleTermExceptions| replace:: :py:class:`MultipleTermExceptions <parse_ebnf.parsing.MultipleTermExceptions>`
.. |MultipleTermPrimariesError| replace:: :py:class:`MultipleTermPrimariesError <parse_ebnf.parsing.MultipleTermPrimariesError>`
.. |UnexpectedLiteralError| replace:: :py:class:`UnexpectedLiteralError <parse_ebnf.parsing.UnexpectedLiteralError>`
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
