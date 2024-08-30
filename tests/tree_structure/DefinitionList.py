from tests.tree_structure import literal, predicate, either, zero_or_more, maybe
from parse_ebnf.nodes import *

parents = [ Product, Repeat, Option, Group ]
children = [ zero_or_more(maybe(Space), Definition, maybe(Space), literal(["|", "/", "!"])), maybe(Space), maybe(Definition), maybe(Space) ]
