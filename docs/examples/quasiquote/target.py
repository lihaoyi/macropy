from docs.examples.quasiquote.macro_module import expand


func = (expand(1 + 2))
print func(5)