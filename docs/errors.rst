.. _errors:
.. index:: errors

Errors
======

Every error in this package inherits from the following class:

.. autoclass:: parse_ebnf.EBNFError

Errors only occur during parsing, all of them inherit from:

.. autoclass:: parse_ebnf.parsing.ParsingError

Parsing errors reference
------------------------

.. autoclass:: parse_ebnf.parsing.EOFError
.. autoclass:: parse_ebnf.parsing.UnexpectedCharacterError
.. autoclass:: parse_ebnf.parsing.NoSpaceError
.. autoclass:: parse_ebnf.parsing.NoLiteralError
.. autoclass:: parse_ebnf.parsing.UndelimitedTermError
.. autoclass:: parse_ebnf.parsing.MultipleTermRepetitions
.. autoclass:: parse_ebnf.parsing.MultipleTermExceptions
.. autoclass:: parse_ebnf.parsing.MultipleTermPrimariesError
.. autoclass:: parse_ebnf.parsing.UnexpectedLiteralError

Handling parsing errors
-----------------------

Parsing errors can be handled gracefully, upon which a :ref:`partial parse tree
will be generated <partial>`. Do do so, wrap your parsing function in a ``try``
block and except |ParsingError|:

.. code-block:: python

   try
        #Your parsing function here
   except parse_ebnf.parsing.ParsingError as e:
        pt = e.parser.pt
        #Make sure to mark the fact that the tree is partial! You cannot easily
        #tell if a tree is partial just by looking at it.
        partial = True
