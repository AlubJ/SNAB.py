import struct
import sys

from SNAB import SNABRead, SNABWrite
from SNAB.registry import GLOBAL_REGISTRY

simpleStruct = {
    "string": "This is a string value!",
    "real": 2.184,
    "int": 1851,
    "undefined": None,
    "null": None,
}

simpleArray = [
    "This is an array,",
    2.184,
    1851,
    None,
    None,
]

nestedStruct = {
    "nested_struct": {
        "test": "I am a nested struct!",
        "int": 1851,
        "real": 2.184,
        "undefined": None,
        "null": None,
    },
    "nested_array": [
        "I am a nested array!",
        2.184,
        1851,
        None,
        None,
    ],
}

megaTest = {
    "string": "hello world",
    "int": 42,
    "float": 3.14159,
    "bool_true": True,
    "bool_false": False,
    "none": None,

    "list_mixed": [
        1,
        "two",
        3.0,
        False,
        None,
        [10, 20, 30],
        {"inner_key": "inner_value"},
    ],

    "dict_simple": {
        "a": 1,
        "b": 2,
        "c": 3,
    },

    "dict_nested": {
        "level_1": {
            "level_2": {
                "level_3": {
                    "value": "deep",
                    "numbers": [1, 2, 3, 4, 5],
                }
            }
        }
    },

    "users": [
        {
            "id": 1,
            "name": "Alice",
            "active": True,
            "roles": ["admin", "editor"],
            "profile": {
                "email": "alice@example.com",
                "age": 30,
                "preferences": {
                    "theme": "dark",
                    "notifications": True,
                },
            },
        },
        {
            "id": 2,
            "name": "Bob",
            "active": False,
            "roles": [],
            "profile": {
                "email": None,
                "age": None,
                "preferences": {},
            },
        },
    ],

    "numbers": {
        "small": [0, 1, -1],
        "large": [10**5, 10**10, -10**10],
        "floats": [0.1, -0.001, 1e6],
    },

    "matrix": [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ],

    "empty_structures": {
        "empty_list": [],
        "empty_dict": {},
        "empty_string": "",
    },

    "heterogeneous_array": [
        {"type": "point", "x": 1, "y": 2},
        {"type": "circle", "radius": 5.5},
        {"type": "polygon", "points": [(0,0), (1,0), (1,1)]},
    ],

    "flags": {
        "bitmask": 0b101010,
        "hex": 0xFF,
        "octal": 0o755,
    },

    "binary_like": {
        "bytes": b"\x00\x01\x02\xFF",
        "bytearray": bytearray([0, 1, 2, 255]),
    },

    "deep_list_nesting": [[[[[["too deep"]]]]]],

    "config": {
        "version": "1.2.3",
        "enabled": True,
        "thresholds": {
            "warning": 70,
            "error": 90,
        },
        "paths": [
            "/tmp",
            "/var/log",
            "/home/user",
        ],
    },
}

snab_bytes = SNABWrite(simpleStruct, compress=False, endianness="little")
with open("simple-struct.snab", "wb") as f:
    f.write(snab_bytes)

snab_bytes = SNABWrite(simpleStruct, compress=True, endianness="little")
with open("simple-struct-compressed.snab", "wb") as f:
    f.write(snab_bytes)

snab_bytes = SNABWrite(simpleArray, compress=False, endianness="little")
with open("simple-array.snab", "wb") as f:
    f.write(snab_bytes)

snab_bytes = SNABWrite(simpleArray, compress=True, endianness="little")
with open("simple-array-compressed.snab", "wb") as f:
    f.write(snab_bytes)

snab_bytes = SNABWrite(nestedStruct, compress=False, endianness="little")
with open("nested-struct.snab", "wb") as f:
    f.write(snab_bytes)

snab_bytes = SNABWrite(nestedStruct, compress=True, endianness="little")
with open("nested-struct-compressed.snab", "wb") as f:
    f.write(snab_bytes)

snab_bytes = SNABWrite(megaTest, compress=False, endianness="little")
with open("mega-test.snab", "wb") as f:
    f.write(snab_bytes)

snab_bytes = SNABWrite(megaTest, compress=True, endianness="little")
with open("mega-test-compressed.snab", "wb") as f:
    f.write(snab_bytes)