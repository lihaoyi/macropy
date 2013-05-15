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

/** python-style classes in javascript!! **/

var to_array = function to_array(a){return Array.prototype.slice.call(a,0);};

function instancemethod(cls, fn) {
    var meta = function $_instancemethod() {
        /*
        if (!__builtins__.isinstance(arguments[0], cls))
            throw new Error('TypeError: unbound method '+fn.__name__+'() must be called with '+cls.__name__+' instance as the first argument');
        */
        return fn.apply(null, arguments);
    }
    meta.__name__ = fn.__name__?fn.__name__:fn.name;
    meta.__type__ = instancemethod;
    meta.__wraps__ = fn;
    fn.__wrapper__ = meta;
    meta.__str__ = function str(){
        return '<unbound method '+cls.__name__+'.'+meta.__name__+'>';
    };
    meta.im_class = cls;
    meta.im_func = fn;
    meta.im_self = null;
    meta.__get__ = function $_get(self, ncls) {
        ncls = ncls||self.__class__;
        /*
        if (!__builtins__.isinstance(self, cls))
            throw new Error('idk what just happened... invalid self while binding instancemethod');
        */
        var m2 = function() {
            return fn.apply(this, [self].concat(to_array(arguments)));
        };
        m2.__name__ = meta.__name__;
        m2.__type__ = instancemethod;
        m2.__wraps__ = fn;
        fn.__wraper__ = fn;
        m2.__str__ = function(){
            return $b.str('<bound method '+ncls.__name__+'.'+meta.__name__+' of '+$b.str(self)+'>');
        };
        m2.im_class = ncls;
        m2.im_func = fn;
        m2.im_self = self;
        m2.args = function $_args(pos, kwd) {
            if (pos.__class__)
               pos = __builtins__.tuple([self]).__add__(pos);
            else
               pos = [self].concat(pos);
            return fn.args(pos, kwd);
        };
        m2.args.__name__ = meta.__name__;
        return m2;
    };
    return meta;
}

function _set_name(fn, name) {
    fn.__name__ = name;
    while(fn = fn.__wraps__)
        fn.__name__ = name;
}

var type = $def(function type(name, bases, namespace) {
    var cls = function $_type() {
        var self = function () {
            if (self.__call__) {
                return self.__call__.apply(this, arguments);
            } else {
                $b.raise($b.TypeError($b.str(self).as_js() + ' has no attribute __call__'));
            }
        };
        self.__init__ = instancemethod(cls, function(){}).__get__(self);
        self.__class__ = cls;
        self.__type__ = 'instance';

        for (var attr in cls) {
            if (['__type__','__class__'].indexOf(attr)!==-1)
              continue;
            var val = cls[attr];
            if (val && val.__type__ == instancemethod && !val.im_self) {
                self[attr] = val.__get__(self, cls);
                _set_name(self[attr], attr);
            } else {
                self[attr] = val;
            }
        }
        self.__init__.apply(null, arguments);
        self._old_toString = self.toString;
        if (self.__str__)
            self.toString = function(){ return self.__str__()._data; };
        return self;
    };
    var ts = cls.toString;
    var __setattr__ = $def(function class_setattr(key, val) {
        if (val && val.__type__ === 'function' ||
                (val && !val.__type__ && typeof(val)==='function')) {
            cls[key] = instancemethod(cls, val);
            cls[key]._depth = 1;
        } else if (val && val.__type__ === classmethod) {
            cls[key] = val.__get__(cls);
        } else if (val && val.__type__ === staticmethod) {
            cls[key] = val.__get__(cls);
        } else if (val && val.__type__ === instancemethod) {
            cls[key] = instancemethod(cls, val.im_func);
            cls[key]._depth = val._depth + 1;
        } else
            cls[key] = val;
    });
    for (var i = bases.length - 1; i >= 0; i--) {
        for (var key in bases[i]) {
            if (key === 'prototype') continue;
            var val = bases[i][key];
            if (cls[key] && cls[key]._depth && val._depth && cls[key]._depth < val._depth + 1) {
                continue;
            }
            __setattr__(key, val);
        }
    }
    cls.__type__ = 'type';
    cls.__bases__ = bases;
    cls.__name__ = name;
    for (var key in namespace) {
        __setattr__(key, namespace[key]);
    }
    //if (cls.toString === ts)
    //  cls.toString = cls.__str__;
    return cls;
});

function classmethod(val) {
    var clsm = {};
    clsm.__get__ = function(cls) {
        return instancemethod(cls, val).__get__(cls);
    };
    clsm.__type__ = classmethod;
    clsm.__str__ = function(){return '<classmethod object at 0x10beef01>';};
    return clsm;
}
/*
function __classmethod(cls, val){
    var fn = function() {
        return val.apply(this, [cls].concat(to_array(arguments)));
    };
    if (val.args) {
        fn.args = function(pos, kwd) {
            return val.args([cls].concat(pos), kwd);
        };
    }
    fn.__type__ = 'classmethod';
    fn.__wraps__ = val;
    return fn;
}

// decorators
function classmethod(method){
    method.__cls_classmethod = true;
    return method;
}
*/
function staticmethod(method){
    var obj = {};
    obj.__type__ = staticmethod;
    var blessed = function() {
        return method.apply(null, arguments);
    };
    blessed.__type__ = 'blessed_static';
    obj.__get__ = function(){
        return blessed;
    };
    obj.__str__ = function(){return '<staticmethod object at 0x10beef01>';};
    return obj;
}

var Class = type;

