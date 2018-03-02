.. _pyxl_snippets:

Pyxl Snippets
-------------

.. code:: python

  from macropy.experimental.pyxl_strings import macros, p

  image_name = "bolton.png"
  image = p['<img src="/static/images/{image_name}" />']

  text = "Michael Bolton"
  block = p['<div>{image}{text}</div>']

  element_list = [image, text]
  block2 = p['<div>{element_list}</div>']

  assert block2.to_string() == '<div><img src="/static/images/bolton.png" />Michael Bolton</div>'


`Pyxl <https://github.com/dropbox/pyxl>`_ is a way of integrating XML
markup into your Python code. By default, pyxl hooks into the python
UTF-8 decoder in order to transform the source files at load-time. In
this, it is similar to how MacroPy transforms source files at import
time.

A major difference is that Pyxl by default leaves the HTML fragments
directly in the source code:

.. code:: python

  image_name = "bolton.png"
  image = <img src="/static/images/{image_name}" />

  text = "Michael Bolton"
  block = <div>{image}{text}</div>

  element_list = [image, text]
  block2 = <div>{element_list}</div>


While the MacroPy version requires each snippet to be wrapped in a
``p["..."]`` wrapper. This :repo:`three-line-of-code macro
<macropy/experimental/pyxl_strings.py>` simply uses pyxl as a macro
(operating on string literals), rather than hooking into the UTF-8
decoder. In general, this demonstrates how easy it is to integrate an
"external" DSL into your python program: MacroPy handles all the
intricacies of hooking into the interpreter and intercepting the
import workflow. The programmer simply needs to provide the
source-to-source transformation, which in this case was already
provided.
