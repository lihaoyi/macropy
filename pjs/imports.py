import ast
from converter import register as converts
import utils

IMPORT_TEMPLATE = '''if (__pjs_tmp_module%(subs)s.__all__ === undefined) {
    for (var __pjs_k in __pjs_tmp_module%(subs)s) {
        if (__pjs_k.indexOf('__') !== 0) {
            eval('%(prefix)s' + __pjs_k + ' = __pjs_tmp_module%(subs)s.' + __pjs_k + ';');
        }
    }
    delete __pjs_k;
} else {
    var __pjs_a = __pjs_tmp_module%(subs)s.__all__.as_js();
    for (var __pjs_i=0; __pjs_i<__pjs_a.length; __pjs_i++) {
        var __pjs_k = __pjs_a[__pjs_i];
        eval('%(prefix)s'+__pjs_k+' = __pjs_tmp_module%(subs)s.'+__pjs_k+';');
    }
    delete __pjs_a;
    delete __pjs_i;
    delete __pjs_k;
}
'''

@converts(ast.ImportFrom)
def importfrom(conv, node, scope):
    text = 'var __pjs_tmp_module = $b.__import__("%s", _.__name__, _.__file__);\n' % node.module
    base_name = node.module.split('.')[0]
    subs_name = '.'.join(node.module.split('.')[1:])
    if subs_name:
        subs_name = '.' + subs_name
    prefix = utils.local_prefix(scope)
    for alias in node.names:
        if alias.name == '*':
            text += IMPORT_TEMPLATE % {'prefix': prefix, 'subs':subs_name}
            break
        asname = alias.asname or alias.name
        left = utils.lhand_assign(asname, scope)
        text += '%s = __pjs_tmp_module%s.%s;\n' % (left, subs_name, alias.name)
    conv.add_import(node.module)
    return text

@converts(ast.Import)
def _import(conv, node, scope):
    tpl = '%s = $b.__import__("%s", _.__name__, _.__file__);\n'
    text = ''
    for name in node.names:
        asname = name.name.split('.')[0]
        if name.asname:
            raise PJsException('import x as y not yet supported')
            asname = name.asname
        asname = utils.lhand_assign(asname, scope)
        text += tpl % (asname, name.name)
        conv.add_import(name.name)
    return text

# vim: et sw=4 sts=4
