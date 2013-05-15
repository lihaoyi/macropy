import ast
from converter import register as converts, PJsNotImplemented
import utils

WHILE_TPL = '''\
while ($b.bool(%s) === true) {
%s
}
'''

@converts(ast.While)
def _while(conv, node, scope):
    if node.orelse:
        raise PJsNotImplemented('while...else not implemented')
    test = conv.convert_node(node.test, scope)
    body = conv.convert_block(node.body, scope)
    return WHILE_TPL % (test, body)

FOR_TPL = '''\
var %s = $b.foriter(%s);
while (%s.trynext()) {
    %s
%s
}
'''

@converts(ast.For)
def _for(conv, node, scope):
    ible = conv.convert_node(node.iter, scope)
    temp_iter = conv.get_temp('iter')
    if isinstance(node.target, ast.Name):
        targ = utils.lhand_assign(node.target.id, scope)
        assign = '%s = %s.value;\n' % (targ, temp_iter)
    else:
        assign = utils.deepleft(conv, node.target, [], scope, '%s.value' % temp_iter).replace('\n', '\n    ')

    body = conv.convert_block(node.body, scope)

    conv.kill_temp('iter')
    return FOR_TPL % (temp_iter, ible, temp_iter, assign, body)

LCOMP_TMP = '''\
$b.%(ctype)scomp(%(iters)s, function (%(names)s) {return %(elt)s;}, %(ifs)s)'''

@converts(ast.ListComp)
def listComp(conv, node, scope):
    return do_comp(conv, node, scope, 'list')

@converts(ast.GeneratorExp)
def genComp(conv, node, scope):
    return do_comp(conv, node, scope, 'gen')

def do_comp(conv, node, scope, ctype):
    iters = []
    names = []
    ifs = []
    dct = {'ctype': ctype}

    for gen in node.generators:
        if len(gen.ifs) > 1:
            raise PJsNotImplemented('Why would a ListComp generator have multiple ifs? please report this...')
        if not isinstance(gen.target, ast.Name):
            raise PJsNotImplemented('Tuple listcomp targets not supported')
        name = gen.target.id
        if not gen.ifs:
            ifs.append('null')
        else:
            fn_scope = scope.copy()
            fn_scope.locals.append(name)
            ifs.append('function (%s) { return %s; }' % (name, conv.convert_node(gen.ifs[0], fn_scope)))
        iters.append(conv.convert_node(gen.iter, scope))
        names.append(name)

    elt_scope = scope.copy()
    elt_scope.locals += names
    dct['elt'] = conv.convert_node(node.elt, elt_scope)

    dct['iters'] = '[%s]' % ', '.join(iters)
    dct['names'] = ', '.join(names)
    dct['ifs'] = '[%s]' % ', '.join(ifs)
    return LCOMP_TMP % dct

IF_TPL = '''\
if ($b.bool(%(test)s) === true) {
%(contents)s
}%(more)s
'''

@converts(ast.If)
def _if(conv, node, scope):
    dct = {}
    dct['test'] = conv.convert_node(node.test, scope)
    dct['contents'] = conv.convert_block(node.body, scope)
    if node.orelse:
        if len(node.orelse) == 1:
            js = conv.convert_node(node.orelse[0], scope)
            dct['more'] = ' else ' + js
        else:
            js = conv.convert_block(node.orelse, scope)
            dct['more'] = ' else {\n%s\n}' % js
    else:
        dct['more'] = ''
    text = IF_TPL % dct
    return text

TRY_TPL = '''try {
%s
} catch (%s) {
    %s
}
'''

@converts(ast.TryExcept)
def _tryexcept(conv, node, scope):
    single = '''%s{
    %s
    }'''
    body = conv.convert_block(node.body, scope)
    subs = []
    temp = conv.get_temp('err')
    for handler in node.handlers:
        eb = ''
        if handler.name is not None:
            name = utils.lhand_assign(handler.name.id, scope)
            eb = '    %s = %s;\n    ' % (name, temp)
        eb_ = conv.convert_block(handler.body, scope)
        eb += eb_

        if handler.type is not None:
            t = conv.convert_node(handler.type, scope)
            top = 'if (%s.__class__ && $b.isinstance(%s, %s)) ' % (temp, temp, t)
        else:
            top = ''

        subs.append(single % (top, eb))
    text = TRY_TPL % (body, temp, ' else '.join(subs))
    conv.kill_temp('err')
    return text

TRY_FINALLY = '''%(final_temp)s = false;
try {
%(body)s
} catch (%(err_temp)s) {
    try {
        %(excepts)s
    } catch (%(err2_temp)s) {
        %(finally)s
        throw %(err2_temp)s;
    }
    %(final_temp)s = true;
    %(finally)s
}
if (!%(final_temp)s) {
    %(finally)s
}
'''

TRY_FINALLY = '''\
try {
%(body)s
} catch (%(err_temp)s) {
%(finally)s
throw %(err_temp)s;
}
%(finally)s
'''

@converts(ast.TryFinally)
def tryfinally(conv, node, scope):
    dct = {}
    dct['body'] = conv.convert_block(node.body, scope)
    dct['err_temp'] = temp = conv.get_temp('err')
    dct['finally'] = conv.convert_block(node.finalbody, scope)
    conv.kill_temp('err')
    return TRY_FINALLY % dct

# vim: et sw=4 sts=4
