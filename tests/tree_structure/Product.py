from tests.tree_structure import literal, predicate, either, zero_or_more, maybe
from parse_ebnf.nodes import *

parents = [ Root ]
children = [ Identifier, maybe(Space), literal("="), maybe(Space), DefinitionList, maybe(Space), literal([";", "."]) ]
