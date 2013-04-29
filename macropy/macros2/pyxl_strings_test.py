
from macropy.macros2.pyxl_strings import macros, pyxl
from macropy.macros.adt import macros, case, NO_ARG
from pyxl import html
from pyxl.html import rawhtml
import re
import unittest
from xml.etree import ElementTree

def normalize(string):
    return ElementTree.tostring(
        ElementTree.fromstring(
            re.sub("\n *", "", string)
        )
    , encoding='utf8', method='xml')

class Tests(unittest.TestCase):
    def test_inline_python(self):

        image_name = "bolton.png"
        image = pyxl%'<img src="/static/images/{image_name}" />'

        text = "Michael Bolton"
        block = pyxl%'<div>{image}{text}</div>'

        element_list = [image, text]
        block2 = pyxl%'<div>{element_list}</div>'

        assert block2.to_string() == '<div><img src="/static/images/bolton.png" />Michael Bolton</div>'


    def test_dynamic(self):
        items = ['Puppies', 'Dragons']
        nav = pyxl%'<ul />'
        for text in items:
            nav.append(pyxl%'<li>{text}</li>')

        assert str(nav) == "<ul><li>Puppies</li><li>Dragons</li></ul>"

    def test_attributes(self):
        fruit = pyxl%'<div data-text="tangerine" />'
        assert fruit.data_text == "tangerine"
        fruit.set_attr('data-text', 'clementine')
        assert fruit.attr('data-text') == "clementine"


    def test_interpreter(self):
        safe_value = "<b>Puppies!</b>"
        unsafe_value = "<script>bad();</script>"
        unsafe_attr = '">'
        pyxl_blob = pyxl%"""<div class="{unsafe_attr}">
                   {unsafe_value}
                   {rawhtml(safe_value)}
               </div>"""
        target_blob = '<div class="&quot;&gt;">&lt;script&gt;bad();&lt;/script&gt; <b>Puppies!</b></div>'
        assert normalize(pyxl_blob.to_string()) == normalize(target_blob)

    def test_modules(self):
        from pyxl.element import x_element
        @case
        class User(name, profile_picture):
            pass

        class x_user_badge(x_element):
            __attrs__ = {
                'user': object,
            }
            def render(self):
                return pyxl%"""
                    <div>
                        <img src="{self.user.profile_picture}" style="float: left; margin-right: 10px;"/>
                        <div style="display: table-cell;">
                            <div>{self.user.name}</div>
                            {self.children()}
                        </div>
                    </div>"""

        user = User("cowman", "http:/www.google.com")
        content = pyxl%'<div>Any arbitrary content...</div>'
        pyxl_blob = pyxl%'<user_badge user="{user}">{content}</user_badge>'
        target_blob = """
        <div>
            <img src="http:/www.google.com" style="float: left; margin-right: 10px;" />
            <div style="display: table-cell;"><div>cowman</div>
            <div>Any arbitrary content...</div></div>
        </div>"""

        assert normalize(pyxl_blob.to_string()) == normalize(target_blob)



