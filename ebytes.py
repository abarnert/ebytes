import collections.abc
    
class ebytes(bytes):
    def __new__(cls, s, encoding):
        try:
            s = s.encode(encoding)
        except AttributeError:
            pass
        return super().__new__(cls, s)
    def __init__(self, s, encoding):
        self.encoding = encoding
    def __repr__(self):
        return 'ebytes({}, encoding="{}")'.format(super().__repr__(), 
                                                  self.encoding)
    def __str__(self):
        return self.decode(self.encoding)
    def encode(self, encoding):
        return ebytes(self.decode(self.encoding), encoding)
    def change_encoding(self, encoding):
        return ebytes(bytes(self), encoding)
    # NOTE: comparisons are done in terms of self.encoding, _not_ Unicode.
    def _operator(operator):
        operator = '__{}__'.format(operator)
        def method(self, rhs):
            return getattr(bytes, operator)(self, ebytes(rhs, self.encoding))
        return method
    __eq__ = _operator('eq')
    __ne__ = _operator('ne')
    __le__ = _operator('le')
    __lt__ = _operator('lt')
    __ge__ = _operator('ge')
    __gt__ = _operator('gt')
    __add__ = _operator('add')
    del _operator
    def __add__(self, rhs):
        return ebytes(super().__add__(ebytes(rhs, self.encoding)), self.encoding)
    def __radd__(self, lhs):
        try:
            return lhs + str(self)
        except TypeError:
            return NotImplemented
    def _tobytesandback(name):
        def method(self, *args, **kwargs):
            return ebytes(getattr(super(), name)(*args, **kwargs), self.encoding)
        return method
    __mul__ = _tobytesandback('__mul__')
    __rmul__ = _tobytesandback('__rmul__')
    del _tobytesandback
    def _tostr(name):
        def method(self, *args, **kwargs):
            return getattr(str(self), name)(*args, **kwargs)
        return method
    isalpha = _tostr('isalpha')
    isalnum = _tostr('isalnum')
    isdecimal = _tostr('isdecimal')
    isdigit = _tostr('isdigit')
    isidentifier = _tostr('isidentifier')
    islower = _tostr('islower')
    isnumeric = _tostr('isnumeric')
    isprintable = _tostr('isprintable')
    isspace = _tostr('isspace')
    istitle = _tostr('istitle')
    isupper = _tostr('isupper')
    del _tostr
    def _tostrandback(name):
        def method(self, *args, **kwargs):
            return ebytes(getattr(str(self), name)(*args, **kwargs), self.encoding)
        return method
    casefold = _tostrandback('casefold')
    capitalize = _tostrandback('capitalize')
    center = _tostrandback('center')
    expandtabs = _tostrandback('expandtabs')
    format = _tostrandback('format')
    format_map = _tostrandback('format_map')
    ljust = _tostrandback('ljust')
    lower = _tostrandback('lower')
    lstrip = _tostrandback('lstrip')
    rjust = _tostrandback('rjust')
    rsplit = _tostrandback('rsplit')
    rstrip = _tostrandback('rstrip')
    swapcase = _tostrandback('swapcase')
    title = _tostrandback('title')
    upper = _tostrandback('upper')
    zfill = _tostrandback('zfill')
    __mod__ = _tostrandback('__mod__')
    del _tostrandback
    # NOTE: replace, find, is done in terms of self.encoding, _not_ Unicode.
    def replace(self, old, new, count=-1):
        return ebytes(super().replace(ebytes(old, self.encoding),
                                      ebytes(new, self.encoding), count),
                      self.encoding)
    def _argstoebytes(name, maxargs):
        def method(self, *args, **kwargs):
            eargs = (ebytes(arg, self.encoding) 
                     for i, arg in enumerate(args) if i<maxargs)
            return getattr(super(), name)(*eargs, **kwargs)
        return method
    endswith = _argstoebytes('endswith', 1)
    find = _argstoebytes('find', 1)
    index = _argstoebytes('index', 1)
    replace = _argstoebytes('replace', 2)
    startswith = _argstoebytes('startswith', 1)
    del _argstoebytes
    def join(self, iterable):
        return super().join(ebytes(element, self.encoding) for element in iterable)
    def _argstoebyteslist(name, maxargs):
        def method(self, *args, **kwargs):
            eargs = (ebytes(arg, self.encoding) 
                     for i, arg in enumerate(args) if i<maxargs)
            return [ebytes(s, self.encoding)
                    for s in getattr(super(), name)(*eargs, **kwargs)]
        return method
    partition = _argstoebyteslist('partition', 1)
    rpartition = _argstoebyteslist('rpartition', 1)
    rsplit = _argstoebyteslist('rsplit', 1)
    split = _argstoebyteslist('split', 1)
    splitlines = _argstoebyteslist('splitlines', 1)
    del _argstoebyteslist
    def __getitem__(self, index):
        result = super().__getitem__(index)
        if isinstance(result, int):
            return result
        return ebytes(result, self.encoding)
    def translate(self, table):
        if isinstance(table, collections.abc.Mapping):
            return ebytes(str(self).translate(table), self.encoding)
        else:
            return ebytes(bytes(self).translate(table), self.encoding)

def test():
    import io
    s1 = ebytes('\u00e9', 'utf-8')
    s2 = ebytes(s1, 'latin-1')
    s3 = s1.encode('latin-1')
    s4 = str(s1)
    assert repr(s2) == repr(s3)
    assert s1 == s2 == s3 == s4
    f1 = ebytes('%s', 'utf-8')
    assert f1 % s1 == f1 % s2 == f1 % s4 == s1
    f2 = ebytes('{}', 'utf-8')
    assert f2.format(s1) == f2.format(s4) == s1
    assert s1 + s2 == s1 + s4 == s4 + s1
    bio, sio = io.BytesIO(), io.StringIO()
    assert bio.write(s1) == 2
    assert bio.write(s2) == 1
