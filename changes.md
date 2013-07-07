Changelog
=========

1.0.3
-----
- Error messages are now raised at run-time rather than at import time, with other improvements.
- `@enum` macro now has much better error messages

1.0.2
-----
- Removed unit test from PyPI distribution

1.0.1
-----
- Fixed a bug in `ast_ctx_fixer`
- `gen_sym()` is now `gen_sym(name="sym")`, allowing you to override the base name
- Implemented `macropy.case_classes.enum` macro
- Implemented `macropy.quick_lambda.lazy` and `macropy.quick_lambda.interned` macros

