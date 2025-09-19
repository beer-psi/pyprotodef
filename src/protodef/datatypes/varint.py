# pyright: reportMissingTypeArgument=false
import io
from math import ceil
from typing import IO, TYPE_CHECKING, Final

from construct import Construct, IntegerError, VarInt, stream_read, stream_write

if TYPE_CHECKING:
    from construct import Context

SEGMENT_BITS = 0x7F
CONTINUE_BIT = 0x80


class SizedVarInt(Construct):
    def __init__(self, bits: int, max_bytes: int | None = None):
        super().__init__()

        self._bits: int = bits
        self._mask: int = (1 << bits) - 1
        self._msb_mask: int = 1 << (bits - 1)
        self._last_shift: int = bits // 7 * 7

        extra_bits = bits % 7
        self._disallowed_last_byte_mask: int = (
            (1 << (8 - extra_bits)) - 1
        ) << extra_bits

        if max_bytes is not None:
            self._max_bytes: int = max_bytes
        else:
            self._max_bytes = ceil(self._bits / 7)

    def _parse(self, stream: IO[bytes], _context: "Context", path: str):
        shift = 0
        result = 0
        b = 0

        while True:
            b = stream_read(stream, 1, path)[0]

            if shift == self._last_shift and (b & self._disallowed_last_byte_mask) != 0:
                msg = f"VarInt too large for {self._bits} bits"
                raise IntegerError(msg, path)

            result |= (b & SEGMENT_BITS) << shift

            if (b & CONTINUE_BIT) == 0:
                break

            shift += 7

            if shift >= self._bits:
                msg = f"VarInt too large for {self._bits} bits"
                raise IntegerError(msg, path)

            if shift // 7 >= self._max_bytes:
                msg = f"VarInt too large for {self._max_bytes} bytes"
                raise IntegerError(msg, path)

        result &= self._mask

        return (result ^ self._msb_mask) - self._msb_mask

    def _build(self, obj: object, stream: IO[bytes], _context: "Context", path: str):
        if not isinstance(obj, int):
            msg = f"value {obj} is not an integer"
            raise IntegerError(msg, path)

        if obj < -self._msb_mask:
            msg = f"value {obj} is too small for {self._bits} bits"
            raise IntegerError(msg, path)

        if obj > (self._mask >> 1):
            msg = f"value {obj} is too large for {self._bits} bits"
            raise IntegerError(msg, path)

        n = obj & self._mask
        b = bytearray()

        while n > SEGMENT_BITS:
            b.append(CONTINUE_BIT | (n & SEGMENT_BITS))
            n >>= 7

        b.append(n)

        if len(b) > self._max_bytes:
            msg = f"VarInt too large for {self._max_bytes} bytes"
            raise IntegerError(msg, path)

        stream_write(stream, bytes(b), len(b), path)

        return obj


class SizedZigZag(Construct):
    def __init__(self, bits: int, max_bytes: int | None = None):
        super().__init__()

        self._bits: int = bits
        self._mask: int = (1 << bits) - 1
        self._msb_mask: int = 1 << (bits - 1)
        self._last_shift: int = bits // 7 * 7

        extra_bits = bits % 7
        self._disallowed_last_byte_mask: int = (
            (1 << (8 - extra_bits)) - 1
        ) << extra_bits

        if max_bytes is not None:
            self._max_bytes: int = max_bytes
        else:
            self._max_bytes = ceil(self._bits / 7)

    def _parse(self, stream: IO[bytes], _context: "Context", path: str):
        shift = 0
        result = 0
        b = 0

        while True:
            b = stream_read(stream, 1, path)[0]

            if shift == self._last_shift and (b & self._disallowed_last_byte_mask) != 0:
                msg = f"VarInt too large for {self._bits} bits"
                raise IntegerError(msg, path)

            result |= (b & SEGMENT_BITS) << shift

            if (b & CONTINUE_BIT) == 0:
                break

            shift += 7

            if shift >= self._bits:
                msg = f"VarInt too large for {self._bits} bits"
                raise IntegerError(msg, path)

            if shift // 7 >= self._max_bytes:
                msg = f"VarInt too large for {self._max_bytes} bytes"
                raise IntegerError(msg, path)

        return (result >> 1) ^ -(result & 1)

    def _build(self, obj: object, stream: IO[bytes], context: "Context", path: str):
        if not isinstance(obj, int):
            msg = f"value {obj} is not an integer"
            raise IntegerError(msg, path)

        if obj < -self._msb_mask:
            msg = f"value {obj} is too small for {self._bits} bits"
            raise IntegerError(msg, path)

        if obj > (self._mask >> 1):
            msg = f"value {obj} is too large for {self._bits} bits"
            raise IntegerError(msg, path)

        substream = io.BytesIO()

        VarInt._build(  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            abs(obj) * 2 - ((obj & self._mask) >> (self._bits - 1)),
            substream,
            context,
            path,
        )

        if substream.tell() > self._max_bytes:
            msg = f"VarInt too large for {self._max_bytes} bytes"
            raise IntegerError(msg, path)

        stream.write(substream.getvalue())

        return obj


NATIVE_VARINT_TYPES: Final = {
    "varint": SizedVarInt(32),
    "varint64": SizedVarInt(64),
    "varint128": SizedVarInt(128),
    "zigzag32": SizedZigZag(32),
    "zigzag64": SizedZigZag(64),
}
