
import ast
import re
import os

def multiline(text, convert=True):
    '''convert 'text' to a multiline string (if it contains any \\n's)
    Optionally escaping & and :'''

    if text is None:
        return '""';
    lines = text.split('\n')
    multi = (''.join("'%s\\n' +\n" % line.encode('string_escape') for line\
            in lines[:-1]) + "'%s'" % lines[-1].encode('string_escape'))
    if convert:
        multi = multi.replace('&', '&amp;').replace(':', '&coln;')
    return multi

def fix_undef(text, scope, modlevel=False):
    '''Replace special {:undef:[vbl name]} blocks with the properly scoped
    variable if it's available. Otherwise, if [modlevel], replace then mith
    $b.assertdefined()'''

    prefix = local_prefix(scope)
    for name in scope.locals:
        text = re.sub('{:undef:' + name + ':[^:]*:}', prefix + name, text)

    if modlevel:
        text = re.sub('{:undef:(\w+):([^:]*):}', '$b.assertdefined(\\2\\1, "\\1")', text)
        text = text.replace('&coln;', ':').replace('&amp;', '&')
    return text

def local_prefix(scope):
    '''Get the prefix for local variables'''

    if scope.globals is scope.locals:
        return '_.'
    if scope.explicit_locals:
        return '__%d.' % len(scope.parent_locals)
    return ''

def lhand_assign(name, scope):
    prefix = local_prefix(scope)
    if name in scope.locals:
        return prefix + name
    elif name in scope.explicit_globals:
        return '_.%s' % name

    if not prefix:
        prefix = 'var '
    scope.locals.append(name)
    return prefix + name

localfile = lambda x:os.path.join(os.path.dirname(__file__), x)
reserved_words = open(localfile('data/js_reserved.txt')).read().split()

reserved_words += ['js', 'py']

builtin_words = __builtins__.keys()
builtin_words += ['js', 'py', 'definedor']

def resolve(name, scope):
    if name in ('window', 'js'):
        return name
    elif name in ('float', 'int'):
        return '$b._' + name
    elif name == 'py':
        return '$b.py'
    elif name == 'super':
        raise SyntaxError('Sorry, super is a reserved word in javascript. "super" will never be PJs supported; it requires too much attribute magic to correctly support')
    elif name in reserved_words:
        raise SyntaxError("Sorry, '%s' is a reserved word in javascript." % name)
    elif name in scope.explicit_globals:
        return '_.%s' % name
    elif name in scope.locals:
        if scope.globals is scope.locals:
            return '_.%s' % name
        elif scope.explicit_locals:
            return '__%d.%s' % (len(scope.parent_locals), name)
        return name
    for locs in scope.parent_locals:
        if name in locs[1:]:
            return locs[0] + name
    if name in scope.globals:
        return '_.%s' % name
    elif name in builtin_words:
        return '$b.%s' % name
    else:
        prefix = local_prefix(scope)
        return '{:undef:%s:%s:}' % (name, prefix)

def deepleft(conv, node, at, scope, name='__pjs_tmp'):
    if isinstance(node, ast.Tuple):
        text = ''
        for i,n in enumerate(node.elts):
            text += deepleft(conv, n, at + [i], scope, name)
        return text
    else:
        right = name + ''.join('.__getitem__(%d)' % n for n in at)
        if isinstance(node, ast.Subscript):
            left = conv.get_converter(node)(conv, node, scope, True)
            if left.endswith(' '):
                return left + right + ');\n'
        elif isinstance(node, ast.Name):
            left = lhand_assign(node.id, scope)
        else:
            left = conv.convert_node(node, scope)
        return '%s = %s;\n' % (left, right)

def new_scope(scope):
    scope = scope.copy()
    old_locals = scope['locals']
    scope['locals'] = []
    scope['exp globals'] = []
    if scope['exp locals']:
        old_locals.insert(0, '__%d.' % scope['exp locals'])
    else:
        old_locals.insert(0, '')
    if len(old_locals) > 1:
        scope['parent locals'] = scope['parent locals'] + (tuple(old_locals), )
    return scope

# vim: et sw=4 sts=4
