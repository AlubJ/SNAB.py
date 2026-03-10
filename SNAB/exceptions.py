class SNABError(Exception):
    pass

class SNABFormatError(SNABError):
    pass

class SNABUnsupportedType(SNABError):
    pass