import ast
from converter import register as converts, PJsNotImplemented

@converts(ast.Expr)
def expr(conv, node, scope):
    return conv.convert_node(node.value, scope) + ';\n'

@converts(ast.BoolOp)
def boolop(conv, node, scope):
    bools = {
        ast.And:'&&',
        ast.Or:'||'
    }
    if not bools.has_key(node.op.__class__):
        raise PJsNotImplemented("Boolean operation %s not supported" % node.op, node)

    op = bools[node.op.__class__]
    return (' %s ' % op).join('$b.bool(%s)' % conv.convert_node(value, scope) for value in node.values)

@converts(ast.BinOp)
def binop(conv, node, scope):
    tpl = '$b.%s(%s, %s)'
    op = node.op.__class__.__name__.lower()
    ljs = conv.convert_node(node.left, scope)
    rjs = conv.convert_node(node.right, scope)
    return tpl % (op, ljs, rjs)

@converts(ast.Compare)
def compare(conv, node, scope):
    ops = {
        ast.In:'in',
        ast.NotIn:'not in',
        ast.Gt:'>',
        ast.GtE:'>=',
        ast.Lt:'<',
        ast.LtE:'<=',
        ast.Eq:'==',
        ast.NotEq:'!=',
        ast.IsNot:'!==',
        ast.Is:'==='
    }
    items = [conv.convert_node(node.left, scope)]
    for op, val in zip(node.ops, node.comparators):
        if op.__class__ not in ops:
            raise PJsNotImplemented('Comparison operator %s not suported' % op, op)
        items.append("'%s'" % ops[op.__class__])
        js = conv.convert_node(val, scope)
        items.append(js)
    return '$b.do_ops(%s)' % (', '.join(items))

@converts(ast.UnaryOp)
def unaryop(conv, node, scope):
    subs = {
        ast.Not:'!$b.bool(%s)',
        ast.UAdd:'+%s',
        ast.USub:'-%s'
    }
    if node.op.__class__ not in subs:
        raise PJsNotImplemented("Unary op %s not supported" % node.op, node.op)
    return subs[node.op.__class__] % conv.convert_node(node.operand, scope)

# vim: et sw=4 sts=4
