from macropy.tracing import macros, trace
with trace:
    sum = 0
    for i in range(0, 5):
        sum = sum + 5