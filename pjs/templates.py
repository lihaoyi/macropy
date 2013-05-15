
TEMPLATES = {
    'module':'''\
module('%(filename)s', function (%(scope)s) {
    %(scope)s.__doc__ = %(doc)s;
%(contents)s
});
''',
    'class':'''\
%(left)s = %(dec_front)sClass('%(name)s', [%(bases)s], (function(){
    var __%(lnum)s = {};
%(contents)s
    return __%(lnum)s;
}()))%(dec_back)s;
%(rname)s.__module__ = _.__name__;
''',
    'function':'''\
%(left)s = %(dec_front)s$def(%(special)sfunction $_%(name)s(%(args)s) { // %(lineno)d
%(contents)s
})%(dec_back)s;
%(rname)s.__module__ = _.__name__;
%(rname)s.__name__ = $b.str("%(name)s");
''',
    'if':'''\
if ($b.bool(%(test)s) === true) {
%(contents)s
}%(more)s
''',
    'while': '''\
while ($b.bool(%s) === true) {
%s
}
''',
    'for': '''\
var __pjs_iter%d = $b.foriter(%s);
while (__pjs_iter%d.trynext()) {
    %s
%s
}
''',
    'try': '''try {
%s
} catch (__pjs_err) {
    %s
}
''',
    'import *': '''if (__pjs_tmp_module.__all__ === undefined) {
    for (var __pjs_k in __pjs_tmp_module) {
        if (__pjs_k.indexOf('__') !== 0)
            eval('%s'+__pjs_k+' = __pjs_tmp_module.'+__pjs_k+';');
    }
    delete __pjs_k;
} else {
    var __pjs_a = __pjs_tmp_module.__all__.as_js();
    for (var __pjs_i=0; __pjs_i<__pjs_a.length; __pjs_i++) {
        var __pjs_k = __pjs_a[__pjs_i];
        eval('%s'+__pjs_k+' = __pjs_tmp_module.'+__pjs_k+';');
    }
    delete __pjs_a;
    delete __pjs_i;
    delete __pjs_k;
}
'''
}


# vim: et sw=4 sts=4
