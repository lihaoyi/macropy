import ast
from converter import register as converts
import utils

@converts(ast.Name)
def _name(conv, node, scope):
    return utils.resolve(node.id, scope)

@converts(ast.Index)
def _index(conv, node, scope):
    return conv.convert_node(node.value, scope)

@converts(ast.Slice)
def _slice(conv, node, scope):
    if node.lower:
        lower = conv.convert_node(node.lower, scope)
    else:
        lower = 'null'
    if node.upper:
        upper = conv.convert_node(node.upper, scope)
    else:
        upper = 'null'
    if node.step:
        step = conv.convert_node(node.step, scope)
    else:
        step = '1'
    return '$b.slice(%s, %s, %s)' % (lower, upper, step)

# vim: et sw=4 sts=4
