# -*- coding: utf-8 -*-
from macro_module import macros, expand  # noqa: F401

func = expand[1 + 2]
print(func(5))
