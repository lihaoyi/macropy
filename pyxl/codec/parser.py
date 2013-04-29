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

import re
import tokenize
from HTMLParser import HTMLParser

from pyxl import html


class PyxlParser(HTMLParser):

    def __init__(self, row, col, line):
        self.buffer = []
        self.startPos = (row, col)
        self.lastPos = self.startPos
        self.collectedData = ''
        self.row = row
        self.col = col
        self.line = line
        self.openTags = []

        # HTMLParser treats tags in this list like they only
        # contain CDATA. Unfortunately, its regexp isn't the
        # greatest. Also we'd rather treat them like any other
        # tag in pyxl, so we set it to an empty tuple.
        self.CDATA_CONTENT_ELEMENTS = ()

        HTMLParser.__init__(self)

    def feed(self, token):
        ttype, tvalue, tstart, tend, tline = token
        self.line = tline

        # Handle whitespace
        (prev_row, prev_col) = self.lastPos
        (cur_row, cur_col) = tstart
        (end_row, end_col) = tend

        assert cur_row >= prev_row, "Unexpected jump in row"
        self.lastPos = (end_row, end_col)

        # are we now on a new line?
        if cur_row > prev_row:
            self._appendRows(cur_row - prev_row)

        # are we on a multiline statement?
        if end_row > cur_row:
            self._appendRows(end_row - cur_row)

        # interpret jumps on the same line as a single space
        if cur_row == prev_row and cur_col > prev_col:
            HTMLParser.feed(self, ' ')

        if ttype != tokenize.COMMENT:
            HTMLParser.feed(self, tvalue)
        else:
            # comments go directly into the output since they
            # are not a part of the HTML
            self._appendString(tvalue)

    def done(self):
        return not len(self.openTags) and not self.rawdata

    def getToken(self):
        endPos = (self.row, self.col)
        return (tokenize.STRING, ''.join(self.buffer), self.startPos, endPos, '')

    def _appendRows(self, num_rows):
        self.row += num_rows
        self._appendString('\n' * num_rows)
        self.col = 0

    def _appendString(self, string):
        self.buffer.append(string)
        self.col += len(string)

    def _handle_starttag(self, tag, attrs):
        self._handle_enddata()

        if tag == 'if':
            assert len(attrs) == 1, "if tag only takes one attr called 'cond'"
            assert attrs[0][0] == 'cond', "if tag must contain the 'cond' attr"

            self._appendString('bool(')
            self._handle_attr_value(attrs[0][1])
            self._appendString(') and html.x_frag()')
            return

        module, dot, identifier = tag.rpartition('.')
        identifier = 'x_%s' % identifier
        x_tag = module + dot + identifier

        if hasattr(html, x_tag):
            self._appendString('html.')
        self._appendString('%s(' % x_tag)

        first_attr = True
        for attr_name, attr_value in attrs:
            if first_attr: first_attr = False
            else: self._appendString(', ')

            self._appendString(PyxlParser._safeAttrName(attr_name))
            self._appendString('=')
            self._handle_attr_value(attr_value)

        self._appendString(')')

    def _handle_attr_value(self, attr_value):
        text_and_code_parts = self._get_text_and_code_parts(attr_value)
        if len(text_and_code_parts) == 1:
            part, is_code = text_and_code_parts[0]
            if is_code:
                self._appendString(part)
            else:
                self._appendString(repr(part))
        else:
            self._appendString('u"".join((')
            for part, is_code in text_and_code_parts:
                if is_code:
                    self._appendString('unicode(')
                    self._appendString(part)
                    self._appendString(')')
                else:
                    self._appendString(repr(part))
                self._appendString(', ')
            self._appendString('))')

    @staticmethod
    def _safeAttrName(name):
        if name == 'class':
            return 'xclass'
        if name == 'for':
            return 'xfor'
        return name.replace('-', '_').replace(':', 'COLON')

    def handle_startendtag(self, tag, attrs):
        self._handle_starttag(tag, attrs)
        if not len(self.openTags): return
        self._appendString(',')

    def handle_starttag(self, tag, attrs):
        self._handle_starttag(tag, attrs)
        self._appendString('(')
        self.openTags.append((tag, self.row, self.line))

    def handle_endtag(self, tag):
        self._handle_enddata()
        close_tag, row, line = self.openTags.pop()
        assert close_tag == tag, "'%s' closed with '%s'" % (close_tag, tag)

        self._appendString(')')
        if not len(self.openTags): return
        self._appendString(',')

    def handle_data(self, data):
        self.collectedData += data

    def handle_entityref(self, name):
        self.collectedData += '&%s;' % name

    def handle_charref(self, name):
        self.collectedData += '&#%s' % name

    def handle_comment(self, comment):
        self._handle_enddata()
        self._appendString('html.x_html_comment(comment="')
        self._appendString(' '.join(comment.replace('"', '\\"').split()))
        self._appendString('"),')

    def handle_decl(self, decl):
        self._handle_enddata()
        self._appendString('html.x_html_decl(decl="')
        self._appendString(' '.join(decl.replace('"', '\\"').split()))
        self._appendString('"),')

    MS_DECL_NAME_RE = re.compile('if|else|endif', re.I)
    def unknown_decl(self, decl):
        self._handle_enddata()
        # bug in python 2.5 HTMLParser parse_declaration skips
        # ]]> for regular decls and ]> for MS decls forcing us
        # to special case them here
        if self.MS_DECL_NAME_RE.match(decl):
            self._appendString('html.x_html_ms_decl(decl="')
        else:
            self._appendString('html.x_html_marked_decl(decl="')
        self._appendString(' '.join(decl.replace('"', '\\"').split()))
        self._appendString('"),')

    whitespaceRe = re.compile(ur"[\s]+", re.U)
    def _handle_enddata(self):

         # empty multiline data will be ignored
        if (not self.collectedData or
            ('\n' in self.collectedData and not self.collectedData.strip())):
            self.collectedData = ''
            return

        text_and_code_parts = self._get_text_and_code_parts(self.collectedData)
        for part, is_code in text_and_code_parts:
            if is_code:
                self._appendString(part)
            else:
                self._appendString('html.rawhtml(u"')
                self._appendString(part)
                self._appendString('")')
            self._appendString(', ')

        self.collectedData = ''

    TEXT_AND_CODE_RE = re.compile('((?<!\\\\){.*?(?<!\\\\)})', re.S)
    def _get_text_and_code_parts(self, data):
        parts = []
        raw_parts = (part for part in self.TEXT_AND_CODE_RE.split(data.strip('\n')))

        for part in raw_parts:
            if not part: continue

            is_code = part[0] == '{'

            # unescape { and }
            part = part.replace('\}', '}')
            part = part.replace('\{', '{')

            # replace newlines with spaces
            part = part.replace('\n', ' ')
            part = part.replace('\r', ' ')

            if is_code:
                # strip off enclosing {}
                part = part[1:-1]
            else:
                # escape double quote
                part = part.replace('"', '\\"')

            parts.append((part, is_code))

        return parts
