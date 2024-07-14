from tests.tree_structure import literal, predicate, either, zero_or_more, maybe
from parse_ebnf.nodes import *

parents = [ Term, Exception ]
children = [ literal(["[", "(:"]), maybe(Space), DefinitionList, literal(["]", ":)"]) ]
