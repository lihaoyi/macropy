# -*- coding: utf-8 -*-
from macro_module import macros, f, _  # noqa: F401

arg0 = 10

func = f[_ + arg0]

# prints 11, using `gen_sym`. Otherwise it would print `2`
print(func(1))
