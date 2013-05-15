
import ast
import os
import sys
import utils

MODULE_TEMPLATE = '''\
module('%(filename)s', function (_) {
    _.__doc__ = %(doc)s;
%(contents)s
});
'''

class PJsNotImplemented(Exception):pass
class PJsException(Exception):pass

class Scope:
    default_globals = ['__name__', '__doc__', '__file__']

    def __init__(self, other=None):
        self.globals = Scope.default_globals[:]
        self.locals = self.globals
        self.explicit_globals = []
        self.parent_locals = ()
        self.explicit_locals = 0
        self.num_iters = 0
        self.atomic = False
        if other and isinstance(other, Scope):
            self.__dict__ = other.__dict__.copy()

    def copy(self):
        scope = Scope(self)
        old_locals = scope.locals
        scope.locals = []
        scope.explicit_globals = []
        if scope.explicit_locals:
            old_locals.insert(0, '__%d.' % len(scope.parent_locals))
        else:
            old_locals.insert(0, '')
        if len(old_locals) > 1 and self.locals is not self.globals:
            scope.parent_locals += (tuple(old_locals),)
        return scope

def find_import(name, filename):
    curdir = os.path.dirname(filename)
    cd = os.getcwd()
    for dr in sys.path:
        if dr == cd:
            dr = curdir
        fn = os.path.join(curdir, dr)
        for sub in name.split('.')[:-1]:
            if not os.path.exists(os.path.join(fn, sub, '__init__.py')):
                break
            else:
                yield os.path.join(fn, sub, '__init__.py')
            fn = os.path.join(fn, sub)
        else:
            fn = os.path.join(fn, name.split('.')[-1])
            if os.path.exists(os.path.join(fn, '__init__.py')):
                yield os.path.join(fn, '__init__.py')
                return
            elif os.path.exists(fn + '.py'):
                yield fn + '.py'
                return
    raise PJsException('Import not found: %s from file %s' % (name, filename))

class Converter:
    handlers = {}
    indent = 4
    defaults = {
        'indent': 4,
        'ignore_import_errors': False,
    }

    @classmethod
    def register(cls, nodeType):
        '''Decorator helper; returns a decorator for ast.NodeType, which should decorate a callable
        that accepts:
            @param conv: converter instance
            @param node: the current node
            @param scope: the current scope
        '''
        def meta(fn):
            cls.handlers[nodeType] = fn
        return meta

    def __init__(self, filename, **kwargs):
        self.startfile = os.path.abspath(filename)
        self.options = self.defaults.copy()
        self.options.update(kwargs)

        self.temps = {}
        self.to_import = [self.startfile]
        self.current = None

    def parse(self):
        modules = {}
        while len(self.to_import):
            filename = self.to_import.pop()
            if filename in modules:
                continue
            self.current = filename
            modules[filename] = self.convert_module(filename)
        return modules

    def add_import(self, name):
        if name in ('os', 'os.path', 'sys', '__builtin__', '__main__'):
            return
        self.to_import += list(find_import(name, self.current))

    ## Deal with temporary variables
    def get_temp(self, ttype):
        self.temps[ttype] = self.temps.get(ttype, 0) + 1
        return '__pjs_%s_%d' % (ttype, self.temps[ttype])

    def kill_temp(self, ttype):
        self.temps[ttype] -= 1

    def current_temp(self, ttype):
        return '__pjs_%s_%d' % (ttype, self.temps[ttype])

    ## Conversion funcs
    def convert_module(self, filename):
        filename = os.path.abspath(filename)
        text = open(filename).read()
        node = ast.parse(text, filename)
        dct = {
            'filename': filename,
            'doc': utils.multiline(ast.get_docstring(node), False),
        }
        scope = Scope()
        contents = self.convert_block(node.body, scope)
        contents = utils.fix_undef(contents, scope, True)
        dct['contents'] = contents
        return MODULE_TEMPLATE % dct

    def convert_block(self, nodes, scope):
        text = ''.join(self.convert_node(child, scope) for child in nodes).strip()
        return '\n'.join(' '*self.options['indent'] + line for line in text.split('\n'))

    def convert_node(self, node, scope):
        if self.handlers.has_key(node.__class__):
            return self.handlers[node.__class__](self, node, scope)
        raise PJsNotImplemented("Conversion for node type %s is not yet supported." % node.__class__, vars(node))
    
    def get_converter(self, what):
        if hasattr(what, '__class__'):
            what = what.__class__
        return self.handlers[what]

register = Converter.register
