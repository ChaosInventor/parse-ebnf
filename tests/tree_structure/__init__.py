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
    cleaned = clean_args(*args)

    def e(node, index):
        for arg in cleaned:
            try:
                return arg(node, index)
            except AssertionError: continue
        assert False, "Node does not comply with any of the given predicates"

    return e
def zero_or_more(*args):
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
            print(e)
            if re.match("ran out of children", e.args[0], re.I): return
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
