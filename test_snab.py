import struct
import pytest

from SNAB import SNABRead, SNABWrite
from SNAB.registry import GLOBAL_REGISTRY

def test_simple_struct_roundtrip():
    obj = {
        "name": "SNAB",
        "size": 24.0,
        "valid": True,
        "nothing": None,
    }

    data = SNABWrite(obj, compress=False)
    result = SNABRead(data)

    assert result == obj


def test_array_root():
    obj = [1, 2, 3, "hello", False, None]

    data = SNABWrite(obj)
    result = SNABRead(data)

    assert result == obj


def test_nested_structs_and_arrays():
    obj = {
        "a": {
            "b": {
                "c": [1, 2, {"x": "y"}]
            }
        }
    }

    data = SNABWrite(obj)
    result = SNABRead(data)

    assert result == obj


def test_compression_roundtrip():
    obj = {"data": ["hello"] * 100}

    data = SNABWrite(obj, compress=True)
    result = SNABRead(data)

    assert result == obj


def test_big_endian_roundtrip():
    obj = {
        "number": 1234567890123456789,
        "float": 3.14159265359,
    }

    data = SNABWrite(obj, endianness="big")
    result = SNABRead(data)

    assert result == obj


def test_binary_buffer():
    raw = b"\x00\x01\x02\x03\xFF"
    obj = {"bin": raw}

    data = SNABWrite(obj)
    result = SNABRead(data)

    assert result["bin"] == raw

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y


EXT_POINT = 0x80


class PointCodec:
    @staticmethod
    def can_encode(obj):
        return isinstance(obj, Point)

    @staticmethod
    def encode(writer, obj):
        writer.buf.extend(
            struct.pack(writer.endian + "dd", obj.x, obj.y)
        )

    @staticmethod
    def decode(reader):
        x = reader._unpack("d")
        y = reader._unpack("d")
        return Point(x, y)


@pytest.fixture(scope="module", autouse=True)
def register_point_type():
    codec = PointCodec()
    GLOBAL_REGISTRY.register(
        EXT_POINT,
        codec,
        codec
    )


def test_extended_type_roundtrip():
    obj = {
        "p1": Point(1.0, 2.0),
        "p2": Point(-3.5, 9.25)
    }

    data = SNABWrite(obj)
    result = SNABRead(data)

    assert result == obj

def test_invalid_root_raises():
    with pytest.raises(ValueError):
        SNABWrite("not a container")


def test_checksum_validation_error():
    obj = {"x": 1}
    data = bytearray(SNABWrite(obj))
    data[-1] ^= 0xFF  # corrupt stream

    with pytest.raises(Exception):
        SNABRead(bytes(data), validate=True)