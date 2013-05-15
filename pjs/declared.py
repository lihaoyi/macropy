import ast
from converter import register as converts
import utils

@converts(ast.Dict)
def _dict(conv, node, scope):
    return '$b.dict([%s])' % ', '.join('[%s, %s]' % (
            conv.convert_node(key, scope),
            conv.convert_node(value, scope)
        ) for key, value in zip(node.keys, node.values))

@converts(ast.List)
def _list(conv, node, scope):
    return '$b.list([%s])' % ', '.join(conv.convert_node(sub, scope) for sub in node.elts)

@converts(ast.Num)
def _num(conv, node, scope):
    if type(node.n) == float:
        return '$b._float(%s)' % node.n
    return str(node.n)

@converts(ast.Str)
def _str(conv, node, scope):
    return '$b.str(%s)' % utils.multiline(node.s)

@converts(ast.Tuple)
def _tuple(conv, node, scope):
    return '$b.tuple([%s])' % ', '.join(conv.convert_node(sub, scope) for sub in node.elts)

# vim: et sw=4 sts=4
