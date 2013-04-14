
def x(printer, x):
    try:
        printer(x)
    except:
        print x


x(lambda x: log(x), 10)