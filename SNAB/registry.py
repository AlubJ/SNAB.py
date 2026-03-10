class TypeRegistry:
    def __init__(self):
        self._encoders = {}
        self._decoders = {}

    def register(self, indicator, encoder, decoder):
        if not (0x80 <= indicator <= 0xFF):
            raise ValueError("Extended datatypes must be in range 0x80–0xFF")
        self._encoders[indicator] = encoder
        self._decoders[indicator] = decoder

    def encoder(self, indicator):
        return self._encoders.get(indicator)

    def decoder(self, indicator):
        return self._decoders.get(indicator)


GLOBAL_REGISTRY = TypeRegistry()