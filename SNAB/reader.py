import struct, zlib
from .constants import *
from .exceptions import *
from .registry import GLOBAL_REGISTRY
from .header import read_header

class Reader:
    def __init__(self, data, validate=True, max_depth=1024):
        self.validate = validate
        self.max_depth = max_depth

        self.header = read_header(data)
        self.data = data[HEADER_SIZE:HEADER_SIZE+self.header["size"]]

        if validate:
            if zlib.crc32(self.data) != self.header["checksum"]:
                raise SNABFormatError("Checksum mismatch")

        if self.header["compressed"]:
            self.data = zlib.decompress(self.data)

        self.offset = 0
        self.endian = "<" if self.header["endianness"] == 0 else ">"

    def read(self):
        dtype = self._u8()
        if dtype == STRUCT:
            return self._read_struct(0)
        if dtype == ARRAY:
            return self._read_array(0)
        raise SNABFormatError("Root must be struct or array")

    def _read_struct(self, depth):
        if depth > self.max_depth:
            raise SNABFormatError("Max nesting depth exceeded")

        result = {}
        while True:
            dtype = self._u8()
            if dtype == TERMINATOR:
                return result

            key = self._cstring()
            result[key] = self._read_value(dtype, depth + 1)

    def _read_array(self, depth):
        if depth > self.max_depth:
            raise SNABFormatError("Max nesting depth exceeded")

        result = []
        while True:
            dtype = self._u8()
            if dtype == TERMINATOR:
                return result
            result.append(self._read_value(dtype, depth + 1))

    def _read_value(self, dtype, depth):
        if dtype == STRING:
            return self._cstring()
        if dtype == WSTRING:
            return self._wstring()
        if dtype == REAL:
            return self._unpack("d")
        if dtype == INT64:
            return self._unpack("q")
        if dtype == FALSE:
            return False
        if dtype == TRUE:
            return True
        if dtype == NULL:
            return None
        if dtype == UNDEFINED:
            return None
        if dtype == BUFFER:
            size = self._unpack("I")
            return self._bytes(size)
        if dtype == STRUCT:
            return self._read_struct(depth)
        if dtype == ARRAY:
            return self._read_array(depth)

        codec = GLOBAL_REGISTRY.decoder(dtype)
        if codec:
            return codec.decode(self)

        raise SNABUnsupportedType(f"Unknown datatype: {hex(dtype)}")

    # ---- low level helpers ----

    def _u8(self):
        val = self.data[self.offset]
        self.offset += 1
        return val

    def _bytes(self, n):
        b = self.data[self.offset:self.offset+n]
        self.offset += n
        return b

    def _unpack(self, fmt):
        size = struct.calcsize(fmt)
        val = struct.unpack(self.endian + fmt, self._bytes(size))[0]
        return val

    def _cstring(self):
        end = self.data.index(0, self.offset)
        s = self.data[self.offset:end].decode("utf-8")
        self.offset = end + 1
        return s

    def _wstring(self):
        out = bytearray()
        while True:
            pair = self._bytes(2)
            if pair == b"\x00\x00":
                break
            out.extend(pair)
        return out.decode("utf-16-le" if self.endian == "<" else "utf-16-be")