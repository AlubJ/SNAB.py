import struct, zlib
from .exceptions import *
from .constants import *
from .registry import GLOBAL_REGISTRY
from .header import write_header

class Writer:
    def __init__(self, compress=True, endianness="little"):
        self.buf = bytearray()
        self.compress = compress
        self.endian = "<" if endianness == "little" else ">"
        self.flags = 0
        if endianness == "big":
            self.flags |= 0x01

    def write(self, obj):
        if isinstance(obj, dict):
            self._struct(obj)
        elif isinstance(obj, list):
            self._array(obj)
        else:
            raise ValueError("Root must be dict or list")

        data = bytes(self.buf)
        if self.compress:
            data = zlib.compress(data)
            self.flags |= 0x08

        checksum = zlib.crc32(data)
        header = write_header(self.flags, checksum, len(data))
        return header + data

    def _struct(self, d):
        self.buf.append(STRUCT)
        self._encode(d)

    def _array(self, a):
        self.buf.append(ARRAY)
        self._encode(a)

    def _value(self, v, key=None):
        if key is not None:
            self.buf.append(self._type(v))
            self.buf.extend(key.encode() + b"\x00")
        else:
            self.buf.append(self._type(v))

        self._encode(v)

    def _type(self, v):
        if v is None:
            return NULL
        if v is True:
            return TRUE
        if v is False:
            return FALSE
        if isinstance(v, str):
            return STRING
        if isinstance(v, float):
            return REAL
        if isinstance(v, int):
            return INT64
        if isinstance(v, dict):
            return STRUCT
        if isinstance(v, (list, tuple)):
            return ARRAY
        if isinstance(v, (bytes, bytearray)):
            return BUFFER

        for t, enc in GLOBAL_REGISTRY._encoders.items():
            if enc.can_encode(v):
                self.flags |= 0x04
                return t

        raise ValueError(f"Unsupported type: {type(v)}")

    def _encode(self, v):
        if v is None:
            return

        if v is False or v is True:
            return
            
        if isinstance(v, str):
            self.buf.extend(v.encode("utf-8") + b"\x00")

        elif isinstance(v, float):
            self.buf.extend(struct.pack(self.endian + "d", v))

        elif isinstance(v, int):
            self.buf.extend(struct.pack(self.endian + "q", v))

        elif isinstance(v, (bytes, bytearray)):
            self.buf.extend(struct.pack(self.endian + "I", len(v)))
            self.buf.extend(v)

        elif isinstance(v, dict):
            for k, val in v.items():
                dtype = self._type(val)
                self.buf.append(dtype)
                self.buf.extend(k.encode("utf-8") + b"\x00")
                self._encode(val)
            self.buf.append(TERMINATOR)

        elif isinstance(v, (list, tuple)):
            for val in v:
                dtype = self._type(val)
                self.buf.append(dtype)
                self._encode(val)
            self.buf.append(TERMINATOR)

        else:
            for t, enc in GLOBAL_REGISTRY._encoders.items():
                if enc.can_encode(v):
                    self.flags |= 0x02
                    self.flags |= 0x04
                    enc.encode(self, v)
                    return

            raise ValueError(f"Unsupported type: {type(v)}")