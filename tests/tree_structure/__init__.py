import inspect
import re
import parse_ebnf.nodes

#TODO: Perfect tree by not allowing the last or first node to ever be a
#space, with the exception of the root

def clean_args(*args):
    ret = []
    for arg in args:
        if inspect.isclass(arg):
            def i(t):
                def instance(node, index):
                    assert index < len(node.children), "Ran out of children nodes for predicate"
                    assert isinstance(node.children[index], t)
                    return index + 1

                return instance
            ret.append(i(arg))
        else: ret.append(arg)
    return ret
def literal(s):
    """A singe |Literal| instance is expected.

    The data that the |Literal| holds is either one of the arguments.
    """
    def l(node, index):
        assert index < len(node.children), "Ran out of children nodes for literal"

        assert isinstance(node.children[index], parse_ebnf.nodes.Literal)
        if isinstance(s, str):
            assert node.children[index].data == s
        else:
            for string in s:
                if node.children[index].data == string: return index + 1
            assert False, "Literal does not contain any of the specified strings"
        return index + 1

    return l
def predicate(*args):
    cleaned = clean_args(*args)

    def p(node, index):
        i = index
        for arg in cleaned:
            i = arg(node, i)

        return i

    return p
def either(*args):
    """Only one of the arguments are expected.

    The arguments may be node types or other functions. In any case, only one of
    them may follow in the child list.
    """
    cleaned = clean_args(*args)

    def e(node, index):
        for arg in cleaned:
            try:
                return arg(node, index)
            except AssertionError: continue
        assert False, "Node does not comply with any of the given predicates"

    return e
def zero_or_more(*args):
    """Any finite number or zero of the arguments are expected.

    Any number of node types and functions may be specified. In all cases, they
    are expected to follow in the child list in the order they are specified.

    For example:

    .. code-block:: py

       zero_or_more(either(Comment, Product), Space)

    Means that either a |Comment| or |Product| followed by a |Space| are
    expected to occur any number of times in the child list.
    """
    cleaned = clean_args(*args)

    def a(node, index):
        i = index
        p = predicate(*args)
        try:
            i = p(node, i)
        except AssertionError: return i
        while i >= 0 and i < len(node.children):
            try:
                i = p(node, i)
            except AssertionError: break
        return i

    return a
def maybe(*args):
    """The arguments may or may not occur.

    The arguments may be node types or other functions. In all cases, either all
    of the arguments occur in the child list in the specified order or they do
    not occur at all.

    For example:

    .. code-block:: py

       maybe(Space, zero_or_more(Term, Product), Space)

    Means that a single sequence of a |Space| followed by any number of |Term|,
    |Product| pairs followed by a single |Space| may occur in the child list, or
    not at all.
    """
    def m(node, index):
        if index >= len(node.children): return index
        p = predicate(*args)
        try:
            return p(node, index)
        except AssertionError: return index

    return m
def check_node_children(node, partial, *args):
    i = 0
    p = predicate(*args)
    newIndex = 0
    try:
        newIndex = p(node, i)
    except AssertionError as e:
        if partial:
            #TODO: Less horrible way of doing this?
            if len(e.args) > 0 and re.match("ran out of children", e.args[0], re.I):
                return
            #TODO: newIndex is not actually updated when an exception is raised,
            #it is always zero. Fix this and check if the predicate that raised
            #the exception was examining the last node.
            elif node.children[newIndex] is node.children[-1]: return
            else: raise e
        else: raise e
    assert newIndex >= 0, "Error while checking node children"
    assert newIndex == len(node.children), "Did not check all node children, too many"
def parent_is_either(node, *args):
    ret = False
    for arg in args:
        if isinstance(node.parent, arg): ret = True

    return ret
