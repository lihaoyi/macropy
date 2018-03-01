# -*- coding: utf-8 -*-

import ast
import sys

PY3 = sys.version_info >= (3,)
PY33 = sys.version_info >= (3, 3)
PY34 = sys.version_info >= (3, 4)
PY35 = sys.version_info >= (3, 5)
PY36 = sys.version_info >= (3, 6)

if PY3:
    string_types = (str,)
    xrange = __builtins__['range']
else:
    string_types = (str, unicode)
    xrange = __builtins__['xrange']

if PY34:
    function_nodes = (ast.FunctionDef,)
else:
    function_nodes = (ast.AsyncFunctionDef, ast.FunctionDef)

scope_nodes = function_nodes + (ast.ClassDef,)


def Call(func, args, keywords):
    """A version of ``ast.Call`` that deals with compatibility.

    .. warning::

      Currently it supports only one element for each *args and **kwargs.
    """
    if PY35:
        return ast.Call(func, args, keywords)
    else:
        starargs = [el.value for el in args if isinstance(el, ast.Starred)]
        if len(starargs) > 1:
            raise ValueError("No more than one starargs.")
        starargs = starargs[0]
        kwargs = [el.value for el in keywords if el.arg is None]
        if len(kwargs) > 1:
            raise ValueError("No more than one kwargs.")
        kwargs = kwargs[0]
        args = [el for el in args if el.value is not starargs]
        keywords = [el for el in keywords if el.value is not kwargs]
        return ast.Call(func, args, keywords, starargs, kwargs)
