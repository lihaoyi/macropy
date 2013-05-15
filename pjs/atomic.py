import ast
from converter import register as converts, PJsNotImplemented
import utils

def atomic(fn):
    def meta(conv, node, scope, *args, **kwargs):
        aflag = False
        if not scope.atomic:
            aflag = True
            scope.atomic = True
        text = fn(conv, node, scope, *args, **kwargs)
        if aflag:
            scope.atomic = False
            if text.startswith('js.'):
                text = text[3:]
        return text
    return meta

@converts(ast.Attribute)
@atomic
def attribute(conv, node, scope):
    if node.attr in utils.reserved_words:
        raise SyntaxError("Sorry, '%s' is a reserved word in javascript." % node.attr)
    js = conv.convert_node(node.value, scope)
    if js == 'js':
        return 'js.%s' % (utils.resolve(node.attr, scope))
    return "%s.%s" % (js, node.attr)

@converts(ast.Call)
@atomic
def call(conv, node, scope):
    if isinstance(node.func, ast.Name) and node.func.id == 'new':
        if node.starargs or node.kwargs or node.keywords or len(node.args) != 1:
            raise SyntaxError('the "new" function is reserved, and takes one argument')
        return 'new ' + conv.convert_node(node.args[0], scope)

    left = conv.convert_node(node.func, scope)
    raw_js = left.startswith('js.') or left.startswith('window.')

    if left == 'js': # e.g. js(some_tuff)
        left = '$b.js'

    if node.starargs or node.kwargs or node.keywords:
        if raw_js:
            raise SyntaxError('cannot use *args, **kwds, or a=b in javascript functions')
        right = call_pythonic(conv, node, scope)
    else:
        right = call_args(conv, node, scope, raw_js)
    return left + right

def call_args(conv, node, scope, raw_js=False):
    args = []
    for n in node.args:
        js = conv.convert_node(n, scope)
        if js.startswith('js.'):
            js = js[3:]
        if raw_js:
            ## in a javascript call
            js = '$b.js(%s)' % js
        args.append(js)
    return '(%s)' % ', '.join(args)

def call_pythonic(conv, node, scope):
    args = call_pythonic_args(conv, node, scope)
    kwds = call_pythonic_keywords(conv, node, scope)
    return '.args(%s, %s)' % (args, kwds)

def call_pythonic_args(conv, node, scope):
    if node.args:
        args = []
        for n in node.args:
            args.append(conv.convert_node(n, scope))
        ret = '$b.tuple([%s])' % ', '.join(args)
        if node.starargs:
            ret += '.__add__($b.tuple(%s))' % conv.convert_node(node.starargs, scope)
        return ret

    elif node.starargs:
        return conv.convert_node(node.starargs, scope)

    else:
        return '$b.tuple([])'

def call_pythonic_keywords(conv, node, scope):
    if node.keywords:
        kargs = []
        for kw in node.keywords:
            kargs.append("'%s': %s" % (kw.arg, conv.convert_node(kw.value, scope)))
        kwds = '{%s}' % ', '.join(kargs)
        if node.kwargs:
            ## duplicates get overridden by kwargs
            kwds += '.extend(%s)' % conv.convert_node(node.kwargs, scope)
        return kwds

    elif node.kwargs:
        return conv.convert_node(node.kwargs, scope)

    else:
        return '{}'

@converts(ast.Subscript)
@atomic
def subscript(conv, node, scope, onleft=False):
    left = conv.convert_node(node.value, scope)
    raw_js = left.startswith('js.') or left.startswith('window.')

    if isinstance(node.slice, ast.Slice) and node.slice.step is None:
        if raw_js:
            if onleft:
                raise SyntaxError('Javascript doesn\'t support slice assignment')
            return slice_js_nostep(conv, left, node, scope)
        
        if node.slice.upper is not None:
            return slice_nostep(conv, left, node, scope, onleft)

    idex = conv.convert_node(node.slice, scope)

    if raw_js:
        if isinstance(node.slice, ast.Slice):
            raise SyntaxError('no steps in javascript slices')
        # TODO check idex for literal
        return '%s[$b.js(%s)]' % (left, idex)

    if onleft == 'delete':
        return '%s.__delitem__(%s)' % (left, idex)
    elif onleft:
        return '%s.__setitem__(%s, ' % (left, idex)
    return '%s.__getitem__(%s)' % (left, idex)

def slice_js_nostep(conv, left, node, scope):
    if node.slice.lower:
        lower = conv.convert_node(node.slice.lower, scope)
    else:
        lower = 0
    if node.slice.upper is None:
        return '%s.slice(%s)' % (left, lower)
    else:
        upper = conv.convert_node(node.slice.upper, scope)
        return '%s.slice(%s, %s)' % (left, lower, upper)

def slice_nostep(conv, left, node, scope, onleft):
    upper = conv.convert_node(node.slice.upper, scope)
    if node.slice.lower:
        lower = conv.convert_node(node.slice.lower, scope)
    else:
        lower = 0
    if onleft == 'delete':
        return '%s.__delslice__(%s, %s)' % (left, lower, upper)
    elif onleft:
        return '%s.__setslice__(%s, %s, ' % (left, lower, upper)
    return '%s.__getslice__(%s, %s)' % (left, lower, upper)

# vim: et sw=4 sts=4
