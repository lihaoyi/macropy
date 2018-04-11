# -*- coding: utf-8 -*-
from functools import reduce

from macro_module import macros, f, _  # noqa: F401

my_func = f[_ + (1 * _)]
print(my_func(10, 20))  # 30

print(reduce(f[_ + _], [1, 2, 3]))  # 6
print(list(filter(f[_ % 2 != 0], [1, 2, 3])))  # [1, 3]
print(list(map(f[_ * 10], [1, 2, 3])))  # [10, 20, 30]
