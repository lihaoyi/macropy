/**
Copyright 2010 Jared Forsyth <jared@jareforsyth.com>

 Permission is hereby granted, free of charge, to any person
 obtaining a copy of this software and associated documentation
 files (the "Software"), to deal in the Software without
 restriction, including without limitation the rights to use,
 copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following
 conditions:

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 OTHER DEALINGS IN THE SOFTWARE.

**/

/** general module loading... not spectacular, I know; it gets better when you
 * add sys and __builtins__
 **/

var __module_cache = {};
function module(filename, fn) {
    var that = {};
    that.__file__ = filename;
    that.__init__ = fn;
    that.load = $def({'mod':null}, function load_module(name, mod) {
        if (mod === null) mod = {};
        mod.__name__ = name;
        if (__builtins__) mod.__name__ = __builtins__.str(name);
        mod.__file__ = that.__file__;
        if (__builtins__) mod.__file__ = __builtins__.str(that.__file__);
        mod.__dict__ = mod;
        mod.__type__ = 'module';
        that._module = mod;
        fn(mod);
        return mod;
    });
    __module_cache[that.__file__] = that;
}

