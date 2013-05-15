import ast
from converter import register as converts, PJsNotImplemented

@converts(ast.Assert)
def _assert(conv, node, scope):
    js = conv.convert_node(node.test, scope)
    if node.msg:
        msg = conv.convert_node(node.msg, scope)
    else:
        msg = "'%s'" % js.encode('string_escape')
    return '$b.assert(%s, %s);\n' % (js, msg)

# @group jumps

@converts(ast.Break)
def _break(conv, node, scope):
    return 'break;\n'

@converts(ast.Pass)
def _pass(conv, node, scope):
    return ''

@converts(ast.Continue)
def _continue(conv, node, scope):
    return 'continue;\n'

@converts(ast.Return)
def _return(conv, node, scope):
    if node.value is None:
        return 'return;\n'
    return 'return %s;\n' % conv.convert_node(node.value, scope)

@converts(ast.Raise)
def _raise(conv, node, scope):
    if node.type is None:
        return 'throw %s' % conv.current_temp('err')
    js = conv.convert_node(node.type, scope)
    if node.inst is None:
        return '$b.raise(%s);\n' % js
    inner = conv.convert_node(node.inst, scope)
    return '$b.raise(%s(%s));\n' % (js, inner)

@converts(ast.Yield)
def _yield(conv, node, scope):
    raise PJsNotImplemented('Sorry, PJs doesn\'t work with generators, and probably won\'t for the forseeable future...generators are hard.')

@converts(ast.Delete)
def _delete(conv, node, scope):
    t = []
    for tag in node.targets:
        if isinstance(tag, ast.Subscript):
            ## TODO: doesn't handle "delete js.some[3]"
            js = conv.get_converter(tag)(conv, tag, scope, 'delete')
            t.append(js)
        else:
            js = conv.convert_node(tag, scope)
            t.append('delete %s' % js)
    return '\n'.join(t) + '\n'

@converts(ast.Global)
def _global(conv, node, scope):
    js = '// switching to global scope: [%s]\n' % ', '.join(node.names)
    for name in node.names:
        scope.explicit_globals.append(name)
    return js

@converts(ast.Print)
def _print(conv, node, scope):
    if node.dest:
        raise PJsException('print>> is not yet supported')
    values = []
    for child in node.values:
        js = conv.convert_node(child, scope)
        values.append(js)
    text = '$b.print(%s);//, %s\n' % (', '.join(values), str(node.nl).lower())
    return text 

# vim: et sw=4 sts=4
