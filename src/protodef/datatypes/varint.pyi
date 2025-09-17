from typing import Final

from construct import Construct

class SizedVarInt(Construct[int, int]):
    def __init__(self, bits: int) -> None: ...

class SizedZigZag(Construct[int, int]):
    def __init__(self, bits: int) -> None: ...

NATIVE_VARINT_TYPES: Final[dict[str, SizedVarInt | SizedZigZag]]
