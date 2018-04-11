# -*- coding: utf-8 -*-
from .line_number_macro import macros, expand  # noqa:F401


def run(x):
    y = 0
    with expand:
        x = x - 1
        y = 1 / x  # noqa: F841

    return x
