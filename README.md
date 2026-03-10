<h1 align="center">SNAB.py 1.0.0</h1>

<p align="center"><a href="https://github.com/AlubJ/SNAB">SNAB</a> implementation for Python by <a href="https://alub.dev/" target="_blank">Alun Jones</a>.</p>

<!---------------------------------[ Buttons ]---------------------------------->

<div align = center>

[![Badge License]][License]   ![Badge Tests]

</div>

<!---------------------------------------------------------------------------->

[License]: License
[Download]: https://github.com/AlubJ/SNAB.py/release/latest
[Documentation]: https://docs.alub.dev/SNAB.py


<!---------------------------------[ Badges ]---------------------------------->

[Badge License]: https://img.shields.io/badge/License-MIT-blue
[Badge Download]: https://img.shields.io/badge/Download-Latest-red
[Badge Documentation]: https://img.shields.io/badge/Read%20the-Docs-purple
[Badge Tests]: https://img.shields.io/badge/Tests-Passing-green

<!---------------------------------[ Content ]---------------------------------->

---

SNAB.py is a SNAB Specification implementation for Python for serializing and deserializing nested dictionaries and lists.

# Usage
## Writing
```py
from SNAB import SNABRead, SNABWrite

simpleStruct = {
    "string": "This is a string value!",
    "real": 2.184,
    "int": 1851,
    "undefined": None,
    "null": None,
}

snab_bytes = SNABWrite(simpleStruct, compress=False, endianness="little")
with open("simple-struct.snab", "wb") as f:
    f.write(snab_bytes)
```

## Reading
```py
from SNAB import SNABRead, SNABWrite

with open("simple-struct.snab", "rb") as f:
    data = f.read()
    simpleStruct = SNABRead(data)
```

## Custom Datatype
SNAB.py allows for creating custom datatypes for use in the SNAB file.
```py
import struct
from SNAB import SNABRead, SNABWrite
from SNAB.registry import GLOBAL_REGISTRY

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

POINT_TYPE = 0x80

class PointCodec:
    def can_encode(self, obj):
        return isinstance(obj, Point)

    def encode(self, writer, obj):
        writer.buf.extend(
            struct.pack(writer.endian + "dd", obj.x, obj.y)
        )

    def decode(self, reader):
        x = reader._unpack("d")
        y = reader._unpack("d")
        return Point(x, y)

codec = PointCodec()
GLOBAL_REGISTRY.register(POINT_TYPE, codec, codec)
```