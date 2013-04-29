#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import tokenize
from HTMLParser import HTMLParseError
from pyxl.codec.parser import PyxlParser

class PyxlParseError(Exception): pass

def pyxl_untokenize(tokens):
    parts = []
    prev_row = 1
    prev_col = 0

    for token in tokens:
        ttype, tvalue, tstart, tend, tline = token
        row, col = tstart

        if row > prev_row:
            raise PyxlParseError('Unexpected jump in rows (line:%d: %s' % (row, tline))

        # Add whitespace
        col_offset = col - prev_col
        if col_offset > 0:
            parts.append(" " * col_offset)

        parts.append(tvalue)
        prev_row, prev_col = tend

        if ttype in (tokenize.NL, tokenize.NEWLINE):
            prev_row += 1
            prev_col = 0

    return ''.join(parts)

def pyxl_tokenize(readline):
    last_nw_token = None
    prev_token = None

    tokens = tokenize.generate_tokens(readline)
    while 1:
        try:
            token = tokens.next()
        except (StopIteration, tokenize.TokenError):
            break

        ttype, tvalue, tstart, tend, tline = token

        if (ttype == tokenize.OP and tvalue == '<' and last_nw_token and
            ((last_nw_token[0] == tokenize.OP and last_nw_token[1] == '=') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == '(') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == '[') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == '{') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == ',') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == ':') or
             (last_nw_token[0] == tokenize.NAME and last_nw_token[1] == 'print') or
             (last_nw_token[0] == tokenize.NAME and last_nw_token[1] == 'return'))):
            token = get_pyxl_token(token, tokens)

        if ttype not in (tokenize.INDENT,
                         tokenize.DEDENT,
                         tokenize.NL,
                         tokenize.NEWLINE,
                         tokenize.COMMENT):
            last_nw_token = token

        # strip trailing newline from non newline tokens
        if tvalue and tvalue[-1] == '\n' and ttype not in (tokenize.NL, tokenize.NEWLINE):
            ltoken = list(token)
            tvalue = ltoken[1] = tvalue[:-1]
            token = tuple(ltoken)

        # tokenize has this bug where you can get line jumps without a newline token
        # we check and fix for that here by seeing if there was a line jump
        if prev_token:
            prev_ttype, prev_tvalue, prev_tstart, prev_tend, prev_tline = prev_token

            prev_row, prev_col = prev_tend
            cur_row, cur_col = tstart

            # check for a line jump without a newline token
            if (prev_row < cur_row and prev_ttype not in (tokenize.NEWLINE, tokenize.NL)):

                # tokenize also forgets \ continuations :(
                prev_line = prev_tline.strip()
                if prev_ttype != tokenize.COMMENT and prev_line and prev_line[-1] == '\\':
                    start_pos = (prev_row, prev_col)
                    end_pos = (prev_row, prev_col+1)
                    yield (tokenize.STRING, ' \\', start_pos, end_pos, prev_tline)
                    prev_col += 1

                start_pos = (prev_row, prev_col)
                end_pos = (prev_row, prev_col+1)
                yield (tokenize.NL, '\n', start_pos, end_pos, prev_tline)

        prev_token = token
        yield token

def get_pyxl_token(start_token, tokens):
    ttype, tvalue, tstart, tend, tline = start_token
    pyxl_parser = PyxlParser(tstart[0], tstart[1], tline)
    pyxl_parser.feed(start_token)

    for token in tokens:
        ttype, tvalue, tstart, tend, tline = token

        try:
            pyxl_parser.feed(token)
        except HTMLParseError, html_ex:
            msg = 'HTMLParseError: %s (line:%d: %s)' % (html_ex.msg, tstart[0], tline.strip())
            raise PyxlParseError(msg)
        except AssertionError, assert_ex:
            msg = '%s (line:%d: %s)' % (assert_ex, tstart[0], tline.strip())
            raise PyxlParseError(msg)

        if pyxl_parser.done(): break

    if not pyxl_parser.done():
        lines = ['<%s> at (line:%d: %s)' % (tag, row, line.strip())
                 for tag, row, line in pyxl_parser.openTags]
        raise PyxlParseError('Unclosed Tags: %s' % ', '.join(lines))

    return pyxl_parser.getToken()
