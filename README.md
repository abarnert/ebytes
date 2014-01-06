ebytes
======

An encoded bytestring type that tracks its encoding, which can be used (almost everywhere) either a `bytes` or `str` can be used, including mixing the types together.

APIs that require a `bytes` or something that fulfills the buffer API (like writing to a socket or a binary file) treat it as a `bytes`. APIs that require a `str` treat it as a string (decoding automatically).

Mixing an `ebytes` with a `bytes`, `bytearray`, or other buffer-API object treats the latter as an `ebytes` with the same encoding.

Comparison operators and methods that are about searching and the like are byte-based. This includes the `split` family and `replace`. However, case- and formatting-related methods like `islower` or `upper` are Unicode-based.

As with `bytes`, indexing and iteration produce integers, but slicing produces `ebytes`.

Examples
===

    >>> # Construct from a string and encoding
    >>> s1 = ebytes('é', 'utf-8')
    >>> s1
    ebytes(b'\xc3\xa9', encoding="utf-8")
    >>> print(s1)
    'é'
    >>> # ... or from bytes and encoding
    >>> s2 = ebytes(b'\xc3\xa9', 'utf-8')
    >>> s2
    ebytes(b'\xc3\xa9', encoding="utf-8")
    
    >>> # Use it like a bytes
    >>> bio = io.BytesIO()
    >>> bio.write(s1)
    2
    >>> s1[0]
    195
    >>> b'\xc3\xa9' == s1
    True
    >>> s1.translate(bytes.maketrans(b'\xa9\xce', b'ee'))
    ebytes(b'ee', encoding="utf-8")
    
    >>> # Use it like a string
    >>> s1 == 'é'
    True
    >>> 'é' == s1
    True
    >>> s1.isalpha()
    True
    >>> s1.encode('latin-1')
    ebytes(b'\xe9', encoding="latin-1")
    >>> s1.translate({233: 'e'})
    ebytes(b'e', encoding="utf-8")
    
    >>> # Mix and match encodings, even using format or %
    >>> ebytes(b'{}{}', 'utf-8').format('é', ebytes('é', 'latin-1'))
    ebytes(b'\xc3\xa9\xc3\xa9', encoding="utf-8")
    >>> # If you really want mojibake, you have to ask for it:
    >>> s1.change_encoding('latin-1')
    ebytes(b'\xc3\xa9', encoding="latin-1")


Open questions
=====

It's not clear what the `decode` method should do. I left it alone from `bytes`, so if you have, say, an ASCII `ebytes` and you want to try to explicitly decode it as Latin-1, you can. But I'm not sure that's the best decision.

Code that actually requires a `str`, rather than something with a `__str__` method, will not accept an `ebytes`. This is most notable for C-API functions that parse `s`, `U`, etc., like `TextIOWrapper.write`, but Python code that checks `isinstance(s, str)` will fail just as hard. So, the only way to write an `ebytes` to a file is to call `str` on it.

Similarly, code that handles both `str` and `bytes`, but handles them by assuming an encoding for `bytes`, will usually do the wrong thing with an `ebytes`. Again, this notably includes C-API functions that parse `et`, etc., but Python code using `isinstance` or similar C code will have the same problem. Again, the only workaround is to call `str`.

Inheriting from `str` (and storing our data as Unicode and encoding as necessary rather than the other way around) would obviously solve that problem only to create an identical problem with functions that require `bytes` or (more commonly, in C code) the buffer protocol. It might be possible to get around that, at least partially, with a class written in C that could actually support the buffer protocol by encoding on the fly.

For a few of the methods, it's not clear whether they're more search-related or more Unicode-related, so some of the choices of which are implemented via `bytes` calls and which by decoding and using `str` calls may not be ideal.

It might be better for performance to cache the decoded `str` instead of constantly re-creating it. But that may depend on how these things are actually used.
