from tests.tree_structure import literal, predicate, either, zero_or_more, maybe
from parse_ebnf.nodes import *

parents = [ DefinitionList ]
children = [ maybe(Space), zero_or_more(Term, maybe(Space), literal(","), maybe(Space)), maybe(Term, maybe(literal(","))), maybe(Space) ]
