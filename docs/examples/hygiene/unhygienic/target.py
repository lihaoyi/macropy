from docs.examples.hygiene.unhygienic.macro_module import macros, log

buffer = []
def log_func(txt):
    buffer.append(txt)

log[1 + 2 + 3]
log[1 + 2]
# doesn't print anything

print buffer
# ['1 + 2 + 3 -> 6', '1 + 2 -> 3']