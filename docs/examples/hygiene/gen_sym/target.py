from docs.examples.hygiene.gen_sym.macro_module import macros, f, _

arg0 = 10

func = f[_ + arg0]

print func(1)
# 2
# should print 11