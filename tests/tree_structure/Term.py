from tests.tree_structure import literal, predicate, either, zero_or_more, maybe
from parse_ebnf.nodes import *

parents = [ Definition ]
children = [ maybe(Space), maybe(Repetition), maybe(Space), Primary, maybe(Space), maybe(literal("-"), Exception) ]
