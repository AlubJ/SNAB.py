import struct, zlib, uuid
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
        match obj:
            case dict():
                self._struct(obj)
            case list() | tuple():
                self._array(obj)
            case _:
                raise ValueError("Root must be dict or list")

        data = bytes(self.buf)
        if self.compress:
            data = zlib.compress(data)
            self.flags |= 0x08

        checksum = zlib.crc32(data)
        header = write_header(self.flags, checksum, len(data))
        return header + data

    def _struct(self, d):
        self.buf.append(SNABType.STRUCT)
        self._encode(d)

    def _array(self, a):
        self.buf.append(SNABType.ARRAY)
        self._encode(a)

    def _value(self, v, key=None):
        if key is not None:
            self.buf.append(self._type(v))
            self.buf.extend(key.encode() + b"\x00")
        else:
            self.buf.append(self._type(v))

        self._encode(v)

    def _type(self, v):
        match v:
            case None:
                return SNABType.NULL
            case True:
                return SNABType.TRUE
            case False:
                return SNABType.FALSE
            case str():
                return SNABType.STRING
            case float():
                return SNABType.REAL
            case int():
                return SNABType.INT64
            case dict():
                return SNABType.STRUCT
            case list() | tuple():
                return SNABType.ARRAY
            case bytes() | bytearray():
                return SNABType.BUFFER
            case uuid.UUID():
                return SNABType.GUID

        for t, enc in GLOBAL_REGISTRY._encoders.items():
            if enc.can_encode(v):
                self.flags |= 0x04
                return t

        raise ValueError(f"Unsupported type: {type(v)}")

    def _encode(self, v):
        match v:
            case None | True | False:
                return
            case str():
                self.buf.extend(v.encode("utf-8") + b"\x00")
                return
            case float():
                self.buf.extend(struct.pack(self.endian + "d", v))
                return
            case int():
                self.buf.extend(struct.pack(self.endian + "q", v))
                return
            case bytes() | bytearray():
                self.buf.extend(struct.pack(self.endian + "I", len(v)))
                self.buf.extend(v)
                return
            case uuid.UUID():
                match self.endian:
                    case "<":
                        self.buf.extend(v.bytes_le)
                    case ">":
                        self.buf.extend(v.bytes)
                return
            case dict():
                for k, val in v.items():
                    dtype = self._type(val)
                    self.buf.append(dtype)
                    self.buf.extend(k.encode("utf-8") + b"\x00")
                    self._encode(val)
                self.buf.append(SNABType.TERMINATOR)
                return
            case list() | tuple():
                for val in v:
                    dtype = self._type(val)
                    self.buf.append(dtype)
                    self._encode(val)
                self.buf.append(SNABType.TERMINATOR)
                return
            
        for t, enc in GLOBAL_REGISTRY._encoders.items():
            if enc.can_encode(v):
                self.flags |= 0x02
                self.flags |= 0x04
                enc.encode(self, v)
                return

        raise ValueError(f"Unsupported type: {type(v)}")