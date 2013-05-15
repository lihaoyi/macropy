import ast
from converter import register as converts, PJsNotImplemented
import utils

FUNC_TEMPLATE = '''\
%(left)s = %(dec_front)s$def(%(special)sfunction $_%(name)s(%(args)s) { // %(lineno)d
%(contents)s
})%(dec_back)s;
%(rname)s.__module__ = _.__name__;
%(rname)s.__name__ = $b.str("%(name)s");
'''

LAMBDA_TEMPLATE = '''\
$def(%(special)sfunction $_lambda(%(args)s) {return %(contents)s;})'''

CLASS_TEMPLATE = '''\
%(left)s = %(dec_front)sClass('%(name)s', [%(bases)s], (function(){
    var __%(lnum)s = {};
%(contents)s
    return __%(lnum)s;
}()))%(dec_back)s;
%(rname)s.__module__ = _.__name__;
'''

@converts(ast.FunctionDef)
def functiondef(conv, node, scope):
    dct = {
        'name':    node.name,
        'lineno':  node.lineno,

        'special': function_special(conv, node, scope),
        'left':    utils.lhand_assign(node.name, scope),
        'rname':   utils.resolve(node.name, scope),
    }
    args = function_args(conv, node, scope)
    dct['args'] = ', '.join(args)

    dct['dec_front'] = ''
    dct['dec_back'] = ''
    for dec in node.decorator_list:
        dct['dec_front'] += conv.convert_node(dec, scope) + '('
        dct['dec_back'] += ')'

    scope = scope.copy()
    scope.explicit_locals = False
    scope.locals += args

    dct['contents'] = utils.fix_undef(conv.convert_block(node.body, scope), scope)
    return FUNC_TEMPLATE % dct

def function_args(conv, node, scope):
    args = list(arg.id for arg in node.args.args)
    if node.args.vararg:
        args.append(node.args.vararg)
    if node.args.kwarg:
        args.append(node.args.kwarg)
    return args

def function_special(conv, node, scope):
    defaults = function_defaults(conv, node, scope)
    if node.args.kwarg:
        return defaults + ', ' + str(bool(node.args.vararg)).lower() + ', true, '

    elif node.args.vararg:
        return defaults + ', true, '

    elif defaults != '{}':
        return defaults + ', '

    else:
        return ''

def function_defaults(conv, node, scope):
    args = list(arg.id for arg in node.args.args)
    defaults = []
    for default, name in zip(reversed(node.args.defaults), reversed(args)):
        defaults.append("'%s': %s" % (name, conv.convert_node(default, scope)))
    return '{' + ', '.join(defaults) + '}'

@converts(ast.Lambda)
def lambdadef(conv, node, scope):
    dct = {
        'special': function_special(conv, node, scope),
    }
    args = function_args(conv, node, scope)
    dct['args'] = ', '.join(args)
    scope = scope.copy()
    scope.explicit_locals = False
    scope.locals += args
    dct['contents'] = utils.fix_undef(conv.convert_node(node.body, scope), scope)
    return LAMBDA_TEMPLATE % dct

@converts(ast.ClassDef)
def classdef(conv, node, scope):
    imports = []
    dct = {
        'name':  node.name,
        
        'bases': ', '.join(utils.resolve(base.id, scope) for base in node.bases),
        'left':  utils.lhand_assign(node.name, scope),
        'rname': utils.resolve(node.name, scope),
    }

    dct['dec_front'] = ''
    dct['dec_back'] = ''
    for dec in node.decorator_list:
        dct['dec_front'] += conv.convert_node(dec, scope) + '('
        dct['dec_back'] += ')'

    scope = scope.copy()
    scope.explicit_locals = True

    dct['contents'] = utils.fix_undef(conv.convert_block(node.body, scope), scope)

    dct['lnum'] = len(scope.parent_locals)

    return CLASS_TEMPLATE % dct

# vim: et sw=4 sts=4
