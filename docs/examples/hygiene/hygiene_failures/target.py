# -*- coding: utf-8 -*-
from macro_module import macros, f, _  # noqa: F401

arg0 = 10

func = f[_ + arg0]

print(func(1))
# 2
# should print 11
