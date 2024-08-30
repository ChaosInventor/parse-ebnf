from tests.tree_structure import literal, predicate, either, zero_or_more, maybe
from parse_ebnf.nodes import *

parents = [ Root, Comment ]
children = [ literal("(*"), zero_or_more(either(Comment, Text)), literal("*)") ]
