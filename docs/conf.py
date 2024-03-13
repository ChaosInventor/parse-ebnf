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
.. |Node| replace:: :py:class:`Node <parse_ebnf.nodes.Node>`
.. |Root| replace:: :py:class:`Root <parse_ebnf.nodes.Root>`
.. |Text| replace:: :py:class:`Text <parse_ebnf.nodes.Text>`
.. |Comment| replace:: :py:class:`Comment <parse_ebnf.nodes.Comment>`
.. |Space| replace:: :py:class:`Space <parse_ebnf.nodes.Space>`
.. |Identifier| replace:: :py:class:`Identifier <parse_ebnf.nodes.Identifier>`
.. |Literal| replace:: :py:class:`Literal <parse_ebnf.nodes.Literal>`
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
.. |Empty| replace:: :py:class:`Empty <parse_ebnf.nodes.Empty>`
.. |EmptyTerm| replace:: :py:class:`EmptyTerm <parse_ebnf.nodes.EmptyTerm>`

.. |or| replace:: :ref:`| <groups>`
.. |maybe| replace:: :ref:`? <optional>`
.. |any| replace:: :ref:`* <any>`
.. |more| replace:: :ref:`+ <more>`
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
