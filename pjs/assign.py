import ast
from converter import register as converts, PJsNotImplemented
import utils

@converts(ast.Assign)
def assign(conv, node, scope):
    rest = ''
    target = node.targets[0]
    if isinstance(target, ast.Tuple):
        left = 'var __pjs_tmp'
        rest = utils.deepleft(conv, target, [], scope)
    elif isinstance(target, ast.Subscript):
        left = conv.get_converter(target)(conv, target, scope, True)
        if left.endswith(' '):
            return left + conv.convert_node(node.value, scope) + ');\n'
    elif isinstance(target, ast.Name):
        left = utils.lhand_assign(target.id, scope)
    else:
        left = conv.convert_node(target, scope)

    for targ in node.targets[1:]:
        var = left
        if var.startswith('var '):
            var = var[len('var '):]
        if isinstance(targ, ast.Tuple):
            rest += utils.deepleft(conv, targ, [], scope, var)
        elif isinstance(targ, ast.Name):
            mr = utils.lhand_assign(targ.id, scope)
            rest += mr + ' = ' + var + ';\n'
        else:
            rest += '%s = %s;\n' % (conv.convert_node(targ, scope), var)
    js = conv.convert_node(node.value, scope)
    line = '%s = %s;\n' % (left, js)
    return line + rest

@converts(ast.AugAssign)
def _augassign(conv, node, scope):
    tpl = '%s = $b.%s(%s, %s);\n'
    op = node.op.__class__.__name__.lower()
    ljs = conv.convert_node(node.target, scope)
    rjs = conv.convert_node(node.value, scope)
    if isinstance(node.target, ast.Subscript):
        left = conv.get_converter(node.target)(conv, node.target, scope, True)
        if left.endswith(' '):
            return left + conv.convert_node(node.value, scope) + ');\n'
    elif isinstance(node.target, ast.Name):
        left = utils.lhand_assign(node.target.id, scope)
    else:
        left = conv.convert_node(node.target, scope)
    return tpl % (left, op, ljs, rjs)

@converts(ast.AugLoad)
def _augload(node, scope):
    raise PJsNotImplemented('i don\'t know what "AugLoad" is. if you see this, please email jared@jaredforsyth.com w/ code...')

@converts(ast.AugStore)
def _augstore(node, scope):
    raise PJsNotImplemented('i don\'t know what "AugStore" is. if you see this, please email jared@jaredforsyth.com w/ code...')

# vim: et sw=4 sts=4
