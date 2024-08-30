from tests.tree_structure import literal, predicate, either, zero_or_more, maybe
from parse_ebnf.nodes import *

parents = None
children = [ zero_or_more(either(Comment, Product, Space)) ]
