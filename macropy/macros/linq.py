from macropy.core.macros import expr_macro
"""
Aggregate Functions:
    http://www.sqlite.org/lang_aggfunc.html
    avg(x)                  linq.avg
    count(x)                linq.count
    group_concat(x)
    group_concat(x, y)
    max(x)                  max
    min(x)                  min
    sum(x)                  sum
    total(x)                linq.total

Core Functions:
    http://www.sqlite.org/lang_corefunc.html
    abs(x)                  abs
    changes()
    char(x1, x2, ..., xn)
    coalesce(x, y, ...)
    glob(x, y)
    ifnull(x, y)
    instr(x, y)
    hex(x)                  hex
    last_insert_rowid()
    length(x)               len
    like(x, y)
    like(x, y, z)
    load_extension(x)
    load_extension(x, y)
    lower(x)                str.lower
    ltrim(x)                str.lstrip
    ltrim(x, y)             str.lstrip
    max(x, y, ...)          max
    min(x, y, ...)          min
    nullif(x, y)
    quote(x)
    random()                linq.randm
    randomblob(n)
    replace(x, y, z)        str.replace
    round(x)                round
    round(x, y)             round
    rtrim(x)                str.rstrip
    rtrim(x, y)             str.rstrip
    soundex(x)
    sqlite_compileoption_get(n)
    sqlite_comileoption_used(x)
    sqlite_source_id()
    sqlite_version()
    substr(x, y, z)         str[:]
    substr(x, y)            str[:]
    total_changes()
    trim(x)                 str.strip
    trim(x, y)              str.strip
    typeof(x)
    unicode(x)
    upper(x)                str.upper
    zeroblob(n)
"""

@expr_macro
def sql(node):
    pass