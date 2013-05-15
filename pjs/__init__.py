
import converter
from converter import PJsNotImplemented

import utils

import assign
import atomic
import blocks
import declared
import expression
import imports
import scoping
import small
import special

import os
import sys
localfile = lambda *a: os.path.join(os.path.dirname(__file__), *a)

html_out = open(localfile('templates/template.html')).read()
js_out = open(localfile('templates/template.js')).read()
rhino_out = open(localfile('templates/template.ss.js')).read()

def compile(filename, format, **options):
    conv = converter.Converter(filename, **options)
    modules = conv.parse()

    text = '\n'.join(modules[fname] for fname in sorted(modules.keys()))
    lib = os.path.join(options.get('lib_dir', '.'), 'pjslib.js')
    data = {'file':os.path.abspath(filename), 'text':text, 'lib':lib}
    data['path'] = sys.path

    if options.get('rhino', False):
        template = rhino_out
    elif options.get('html', False):
        template = html_out
    else:
        template = js_out

    return template % data

