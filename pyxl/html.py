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

from pyxl.utils import escape
from pyxl.base import x_base

class x_html_element(x_base):
    def _to_list(self, l):
        l.extend((u'<', self.__tag__))
        for name, value in self.__attributes__.iteritems():
            l.extend((u' ', name, u'="', escape(value), u'"'))
        l.append(u'>')

        for child in self.__children__:
            x_base._render_child_to_list(child, l)

        l.extend((u'</', self.__tag__, u'>'))

class x_html_element_nochild(x_base):
    def append(self, child):
        raise Exception('<%s> does not allow children.', self.__tag__)

    def _to_list(self, l):
        l.extend((u'<', self.__tag__))
        for name, value in self.__attributes__.iteritems():
            l.extend((u' ', name, u'="', escape(value), u'"'))
        l.append(u' />')

class x_html_comment(x_base):
    __attrs__ = {
        'comment': unicode,
        }

    def _to_list(self, l):
        pass

class x_html_decl(x_base):
    __attrs__ = {
        'decl': unicode,
        }

    def _to_list(self, l):
        l.extend((u'<!', self.attr('decl'), u'>'))

class x_html_marked_decl(x_base):
    __attrs__ = {
        'decl': unicode,
        }

    def _to_list(self, l):
        l.extend((u'<![', self.attr('decl'), u']]>'))

class x_html_ms_decl(x_base):
    __attrs__ = {
        'decl': unicode,
        }

    def _to_list(self, l):
        l.extend((u'<![', self.attr('decl'), u']>'))

class x_cond_comment(x_base):
    __attrs__ = {
        'cond': unicode,
        }

    def _to_list(self, l):
        # allow '&', escape everything else from cond
        cond = self.__attributes__.get('cond', '')
        cond = '&'.join(map(escape, cond.split('&')))

        l.extend((u'<!--[if ', cond, u']>'))

        for child in self.__children__:
            x_base._render_child_to_list(child, l)

        l.append(u'<![endif]-->')

class x_rawhtml(x_html_element_nochild):
    __attrs__= {
        'text': unicode,
        }

    def _to_list(self, l):
        if not isinstance(self.text, unicode):
            l.append(unicode(self.text, 'utf8'))
        else:
            l.append(self.text)

def rawhtml(text):
    return x_rawhtml(text=text)

class x_frag(x_base):
    def _to_list(self, l):
        for child in self.__children__:
            self._render_child_to_list(child, l)

class x_a(x_html_element):
    __attrs__ = {
        'href': unicode,
        'rel': unicode,
        'type': unicode,
        'name': unicode,
        'target': unicode,
        }

class x_abbr(x_html_element):
    pass

class x_acronym(x_html_element):
    pass

class x_address(x_html_element):
    pass

class x_area(x_html_element_nochild):
    __attrs__ = {
        'alt': unicode,
        'coords': unicode,
        'href': unicode,
        'nohref': unicode,
        'target': unicode,
        }

class x_article(x_html_element):
    pass

class x_aside(x_html_element):
    pass

class x_audio(x_html_element):
    __attrs__ = {
        'src': unicode
        }
        
class x_b(x_html_element):
   pass

class x_big(x_html_element):
   pass

class x_blockquote(x_html_element):
    __attrs__ = {
        'cite': unicode,
        }

class x_body(x_html_element):
    __attrs__ = {
        'contenteditable': unicode,
        }

class x_br(x_html_element_nochild):
   pass

class x_button(x_html_element):
    __attrs__ = {
        'disabled': unicode,
        'name': unicode,
        'type': unicode,
        'value': unicode,
        }

class x_canvas(x_html_element):
    __attrs__ = {
        'height': unicode,
        'width': unicode,
        }

class x_caption(x_html_element):
   pass

class x_cite(x_html_element):
   pass

class x_code(x_html_element):
   pass

class x_col(x_html_element_nochild):
    __attrs__ = {
        'align': unicode,
        'char': unicode,
        'charoff': int,
        'span': int,
        'valign': unicode,
        'width': unicode,
        }

class x_colgroup(x_html_element):
    __attrs__ = {
        'align': unicode,
        'char': unicode,
        'charoff': int,
        'span': int,
        'valign': unicode,
        'width': unicode,
        }

class x_datalist(x_html_element):
    pass

class x_dd(x_html_element):
   pass

class x_del(x_html_element):
    __attrs__ = {
        'cite': unicode,
        'datetime': unicode,
        }

class x_div(x_html_element):
   __attrs__ = {
        'contenteditable': unicode,
       }

class x_dfn(x_html_element):
   pass

class x_dl(x_html_element):
   pass

class x_dt(x_html_element):
   pass

class x_em(x_html_element):
   pass

class x_embed(x_html_element):
    __attrs__ = {
        'src': unicode,
        'width': unicode,
        'height': unicode,
        'allowscriptaccess': unicode,
        'allowfullscreen': unicode,
        'name': unicode,
        'type': unicode,
        }

class x_fieldset(x_html_element):
   pass

class x_footer(x_html_element):
    pass

class x_form(x_html_element):
    __attrs__ = {
        'action': unicode,
        'accept': unicode,
        'accept-charset': unicode,
        'enctype': unicode,
        'method': unicode,
        'name': unicode,
        'target': unicode,
        'novalidate': unicode,
        }

class x_frame(x_html_element_nochild):
    __attrs__ = {
        'frameborder': unicode,
        'longdesc': unicode,
        'marginheight': unicode,
        'marginwidth': unicode,
        'name': unicode,
        'noresize': unicode,
        'scrolling': unicode,
        'src': unicode,
        }

class x_frameset(x_html_element):
    __attrs__ = {
        'rows': unicode,
        'cols': unicode,
        }

class x_h1(x_html_element):
   pass

class x_h2(x_html_element):
   pass

class x_h3(x_html_element):
   pass

class x_h4(x_html_element):
   pass

class x_h5(x_html_element):
   pass

class x_h6(x_html_element):
   pass

class x_head(x_html_element):
    __attrs__ = {
        'profile': unicode,
        }

class x_header(x_html_element):
	pass

class x_hr(x_html_element_nochild):
    pass

class x_html(x_html_element):
    __attrs__ = {
        'content': unicode,
        'scheme': unicode,
        'http-equiv': unicode,
        'xmlns': unicode,
        'xmlns:og': unicode,
        'xmlns:fb': unicode,
        }

class x_i(x_html_element):
   pass

class x_iframe(x_html_element):
    __attrs__ = {
        'frameborder': unicode,
        'height': unicode,
        'longdesc': unicode,
        'marginheight': unicode,
        'marginwidth': unicode,
        'name': unicode,
        'scrolling': unicode,
        'src': unicode,
        'width': unicode,
        # rk: 'allowTransparency' is not in W3C's HTML spec, but it's supported in most modern browsers.
        'allowtransparency': unicode,
        }

class x_video(x_html_element):
    __attrs__ = {
        'autoplay': unicode,
        'controls': unicode,
        'height': unicode,
        'loop': unicode,
        'muted': unicode,
        'poster': unicode,
        'preload': unicode,
        'src': unicode,
        'width': unicode,
        }

class x_img(x_html_element_nochild):
    __attrs__ = {
        'alt': unicode,
        'src': unicode,
        'height': unicode,
        'ismap': unicode,
        'longdesc': unicode,
        'usemap': unicode,
        'vspace': unicode,
        'width': unicode,
        }

class x_input(x_html_element_nochild):
    __attrs__ = {
        'accept': unicode,
        'align': unicode,
        'alt': unicode,
        'autofocus': unicode,
        'checked': unicode,
        'disabled': unicode,
        'list': unicode,
        'max': unicode,
        'maxlength': unicode,
        'min': unicode,
        'name': unicode,
        'pattern': unicode,
        'placeholder': unicode,
        'readonly': unicode,
        'size': unicode,
        'src': unicode,
        'step': unicode,
        'type': unicode,
        'value': unicode,
        'autocomplete': unicode,
        'autocorrect': unicode,
        'required': unicode,
        'spellcheck': unicode,
        'multiple': unicode,
        }

class x_ins(x_html_element):
    __attrs__ = {
        'cite': unicode,
        'datetime': unicode,
        }

class x_kbd(x_html_element):
    pass

class x_label(x_html_element):
    __attrs__ = {
        'for': unicode,
        }

class x_legend(x_html_element):
   pass

class x_li(x_html_element):
   pass

class x_link(x_html_element_nochild):
    __attrs__ = {
        'charset': unicode,
        'href': unicode,
        'hreflang': unicode,
        'media': unicode,
        'rel': unicode,
        'rev': unicode,
        'target': unicode,
        'type': unicode,
        }

class x_map(x_html_element):
    __attrs__ = {
        'name': unicode,
        }

class x_meta(x_html_element_nochild):
    __attrs__ = {
        'content': unicode,
        'http-equiv': unicode,
        'name': unicode,
        'property': unicode,
        "scheme": unicode,
        }

class x_nav(x_html_element):
    pass

class x_noframes(x_html_element):
   pass

class x_noscript(x_html_element):
   pass

class x_object(x_html_element):
    __attrs__ = {
        'align': unicode,
        'archive': unicode,
        'border': unicode,
        'classid': unicode,
        'codebase': unicode,
        'codetype': unicode,
        'data': unicode,
        'declare': unicode,
        'height': unicode,
        'hspace': unicode,
        'name': unicode,
        'standby': unicode,
        'type': unicode,
        'usemap': unicode,
        'vspace': unicode,
        'width': unicode,
        }

class x_ol(x_html_element):
   pass

class x_optgroup(x_html_element):
    __attrs__ = {
        'disabled': unicode,
        'label': unicode,
        }

class x_option(x_html_element):
    __attrs__ = {
        'disabled': unicode,
        'label': unicode,
        'selected': unicode,
        'value': unicode,
        }

class x_p(x_html_element):
   pass

class x_param(x_html_element):
    __attrs__ = {
        'name': unicode,
        'type': unicode,
        'value': unicode,
        'valuetype': unicode,
        }

class x_pre(x_html_element):
   pass

class x_progress(x_html_element):
    __attrs__ = {
        'max': int,
        'value': int,
    }

class x_q(x_html_element):
    __attrs__ = {
        'cite': unicode,
        }

class x_samp(x_html_element):
   pass

class x_script(x_html_element):
    __attrs__ = {
        'async': unicode,
        'charset': unicode,
        'defer': unicode,
        'src': unicode,
        'type': unicode,
        }

class x_section(x_html_element):
	pass

class x_select(x_html_element):
    __attrs__ = {
        'disabled': unicode,
        'multiple': unicode,
        'name': unicode,
        'size': unicode,
        'required': unicode,
        }

class x_small(x_html_element):
   pass

class x_span(x_html_element):
   pass

class x_strong(x_html_element):
   pass

class x_style(x_html_element):
    __attrs__ = {
        'media': unicode,
        'type': unicode,
        }

class x_sub(x_html_element):
   pass

class x_sup(x_html_element):
   pass

class x_table(x_html_element):
    __attrs__ = {
        'border': unicode,
        'cellpadding': unicode,
        'cellspacing': unicode,
        'frame': unicode,
        'rules': unicode,
        'summary': unicode,
        'width': unicode,
        }

class x_tbody(x_html_element):
    __attrs__ = {
        'align': unicode,
        'char': unicode,
        'charoff': unicode,
        'valign': unicode,
        }

class x_td(x_html_element):
    __attrs__ = {
        'abbr': unicode,
        'align': unicode,
        'axis': unicode,
        'char': unicode,
        'charoff': unicode,
        'colspan': unicode,
        'headers': unicode,
        'rowspan': unicode,
        'scope': unicode,
        'valign': unicode,
        }

class x_textarea(x_html_element):
    __attrs__ = {
        'cols': unicode,
        'rows': unicode,
        'disabled': unicode,
        'placeholder': unicode,
        'name': unicode,
        'readonly': unicode,
        'autocorrect': unicode,
        'autocomplete': unicode,
        'autocapitalize': unicode,
        'spellcheck': unicode,
        'autofocus': unicode,
        }

class x_tfoot(x_html_element):
    __attrs__ = {
        'align': unicode,
        'char': unicode,
        'charoff': unicode,
        'valign': unicode,
        }

class x_th(x_html_element):
    __attrs__ = {
        'abbr': unicode,
        'align': unicode,
        'axis': unicode,
        'char': unicode,
        'charoff': unicode,
        'colspan': unicode,
        'rowspan': unicode,
        'scope': unicode,
        'valign': unicode,
        }

class x_thead(x_html_element):
    __attrs__ = {
        'align': unicode,
        'char': unicode,
        'charoff': unicode,
        'valign': unicode,
        }

class x_time(x_html_element):
    __attrs__ = {
        'datetime': unicode,
        }

class x_title(x_html_element):
   pass

class x_tr(x_html_element):
    __attrs__ = {
        'align': unicode,
        'char': unicode,
        'charoff': unicode,
        'valign': unicode,
        }

class x_tt(x_html_element):
    pass

class x_u(x_html_element):
    pass

class x_ul(x_html_element):
    pass

class x_var(x_html_element):
    pass
