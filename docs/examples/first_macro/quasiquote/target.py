from docs.examples.first_macro.quasiquote.macro_module import macros, expand

func = expand[1 + 2]
print func(5)
