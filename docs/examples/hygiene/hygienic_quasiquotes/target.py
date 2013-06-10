from docs.examples.hygiene.hygienic_quasiquotes.macro_module import macros, log

wrap = 3 # try to confuse it

log[1 + 2 + 3]
# 1 + 2 + 3 -> 6
# it still works despite trying to confuse it with `wraps`
