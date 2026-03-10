from .reader import Reader
from .writer import Writer
from .registry import GLOBAL_REGISTRY

def SNABRead(data, validate=True):
    return Reader(data, validate).read()

def SNABWrite(obj, compress=True, endianness="little"):
    return Writer(compress, endianness).write(obj)