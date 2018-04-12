# -*- coding: utf-8 -*-
from macro_module import macros, log  # noqa: F401

wrap = 3  # try to confuse it

log[1 + 2 + 3]
# 1 + 2 + 3 -> 6
# it still works despite trying to confuse it with `wraps`
