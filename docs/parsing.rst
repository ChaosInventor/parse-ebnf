.. _parsing:
.. index:: parsing

Parsing
=======

A parse tree can be created with any of the following functions:

.. autofunction:: parse_ebnf.parse_file
.. autofunction:: parse_ebnf.parse_string
.. autofunction:: parse_ebnf.parse_from_function
.. autofunction:: parse_ebnf.parsing.parse_pt

Parsing individual nodes is not supported.

Parsing state is kept in the following class, that is managed internally and
given in case of :ref:`errors <errors>`:

.. autoclass:: parse_ebnf.parsing.ParserState
