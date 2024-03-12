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
.. |Node| replace:: :py:class:`Node <parse_ebnf.Node>`
.. |Root| replace:: :py:class:`Root <parse_ebnf.Root>`
.. |Text| replace:: :py:class:`Text <parse_ebnf.Text>`
.. |Comment| replace:: :py:class:`Comment <parse_ebnf.Comment>`
.. |Space| replace:: :py:class:`Space <parse_ebnf.Space>`
.. |Identifier| replace:: :py:class:`Identifier <parse_ebnf.Identifier>`
.. |Literal| replace:: :py:class:`Literal <parse_ebnf.Literal>`
.. |Product| replace:: :py:class:`Product <parse_ebnf.Product>`
.. |DefinitionList| replace:: :py:class:`DefinitionList <parse_ebnf.DefinitionList>`
.. |Definition| replace:: :py:class:`Definition <parse_ebnf.Definition>`
.. |Term| replace:: :py:class:`Term <parse_ebnf.Term>`
.. |Exception| replace:: :py:class:`Exception <parse_ebnf.Exception>`
.. |Repetition| replace:: :py:class:`Repetition <parse_ebnf.Repetition>`
.. |Terminal| replace:: :py:class:`Terminal <parse_ebnf.Terminal>`
.. |Repeat| replace:: :py:class:`Repeat <parse_ebnf.Repeat>`
.. |Option| replace:: :py:class:`Option <parse_ebnf.Option>`
.. |Group| replace:: :py:class:`Group <parse_ebnf.Group>`
.. |Special| replace:: :py:class:`Special <parse_ebnf.Special>`
.. |Empty| replace:: :py:class:`Empty <parse_ebnf.Empty>`
.. |EmptyTerm| replace:: :py:class:`EmptyTerm <parse_ebnf.EmptyTerm>`

.. |or| replace:: :ref:`| <groups>`
.. |maybe| replace:: :ref:`? <optional>`
.. |any| replace:: :ref:`* <any>`
.. |more| replace:: :ref:`+ <more>`
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
