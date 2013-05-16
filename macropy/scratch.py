from macropy.macros.tco import macros, tco
@tco
def fact(n, acc=1):
    if n == 0:
        return acc
    else:
        return fact(n-1, n * acc)

print fact(10000)  # doesn't stack overflow