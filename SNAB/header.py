import struct
import zlib
from .constants import HEADER_SIZE, LANGUAGE_ID

def read_header(buf):
    if len(buf) < HEADER_SIZE:
        raise ValueError("Buffer too small for SNAB header")

    (
        major,
        minor,
        flags,
        lang,
        checksum,
        size
    ) = struct.unpack("<BBH4sII", buf[:HEADER_SIZE])

    return {
        "major": major,
        "minor": minor,
        "flags": flags,
        "endianness": (flags & 0x01),
        "extended": bool(flags & 0x02),
        "user": bool(flags & 0x04),
        "compressed": bool(flags & 0x08),
        "language": lang,
        "checksum": checksum,
        "size": size,
    }


def write_header(flags, checksum, size):
    return struct.pack(
        "<BBH4sII",
        1, 0, flags, LANGUAGE_ID, checksum, size
    )