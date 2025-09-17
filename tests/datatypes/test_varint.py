import pytest
from construct import IntegerError, StreamError

from protodef.datatypes.varint import SizedVarInt, SizedZigZag


@pytest.mark.parametrize(
    "bitwidth,data,value",
    [
        (32, b"\x00", 0),
        (32, b"\x01", 1),
        (32, b"\x02", 2),
        (32, b"\x7f", 127),
        (32, b"\x80\x01", 128),
        (32, b"\xff\x01", 255),
        (32, b"\xdd\xc7\x01", 25565),
        (32, b"\xff\xff\x7f", 2097151),
        (32, b"\xff\xff\xff\xff\x07", 2147483647),
        (32, b"\xff\xff\xff\xff\x0f", -1),
        (32, b"\x80\x80\x80\x80\x08", -2147483648),
        (64, b"\x00", 0),
        (64, b"\x01", 1),
        (64, b"\x02", 2),
        (64, b"\x7f", 127),
        (64, b"\x80\x01", 128),
        (64, b"\xff\x01", 255),
        (64, b"\xdd\xc7\x01", 25565),
        (64, b"\xff\xff\x7f", 2097151),
        (64, b"\xff\xff\xff\xff\x07", 2147483647),
        (64, b"\xff\xff\xff\xff\xff\xff\xff\xff\x7f", 9223372036854775807),
        (64, b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01", -1),
        (64, b"\x80\x80\x80\x80\xf8\xff\xff\xff\xff\x01", -2147483648),
        (64, b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01", -9223372036854775808),
    ],
    ids=lambda val: val.hex() if isinstance(val, bytes) else None,  # pyright: ignore[reportAny]
)
def test_sized_varint(bitwidth: int, data: bytes, value: int):
    assert SizedVarInt(bitwidth).parse(data) == value
    assert SizedVarInt(bitwidth).build(value) == data


@pytest.mark.parametrize(
    "bitwidth,value",
    [
        (32, 2147483648),
        (32, -2147483649),
        (32, None),
        (64, 9223372036854775808),
        (64, -9223372036854775809),
        (64, "string"),
    ],
)
def test_sized_varint_build_errors(bitwidth: int, value: object):
    with pytest.raises(IntegerError):
        assert SizedVarInt(bitwidth).build(value)  # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize(
    "bitwidth,data,exc",
    [
        (32, b"\xff\xff\xff\xff", StreamError),
        (32, b"\xff\xff\xff\xff\x10", IntegerError),
        (64, b"\xff\xff\xff\xff\xff\xff\xff\xff", StreamError),
        (64, b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x02", IntegerError),
    ],
)
def test_sized_varint_parse_errors(bitwidth: int, data: object, exc: type[Exception]):
    with pytest.raises(exc):
        assert SizedVarInt(bitwidth).parse(data)  # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize(
    "bitwidth,data,value",
    [
        (32, b"\x00", 0),
        (32, b"\x01", -1),
        (32, b"\x02", 1),
        (32, b"\x7f", -64),
        (32, b"\x80\x01", 64),
        (32, b"\xff\x01", -128),
        (32, b"\xdd\xc7\x01", -12783),
        (32, b"\xff\xff\x7f", -1048576),
        (32, b"\xff\xff\xff\xff\x07", -1073741824),
        (32, b"\xff\xff\xff\xff\x0f", -2147483648),
        (32, b"\x80\x80\x80\x80\x08", 1073741824),
        (64, b"\x00", 0),
        (64, b"\x01", -1),
        (64, b"\x02", 1),
        (64, b"\x7f", -64),
        (64, b"\x80\x01", 64),
        (64, b"\xff\x01", -128),
        (64, b"\xdd\xc7\x01", -12783),
        (64, b"\xff\xff\x7f", -1048576),
        (64, b"\xff\xff\xff\xff\x07", -1073741824),
        (64, b"\xff\xff\xff\xff\xff\xff\xff\xff\x7f", -4611686018427387904),
        (64, b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01", -9223372036854775808),
        (64, b"\x80\x80\x80\x80\xf8\xff\xff\xff\xff\x01", 9223372035781033984),
        (64, b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01", 4611686018427387904),
    ],
    ids=lambda val: val.hex() if isinstance(val, bytes) else None,  # pyright: ignore[reportAny]
)
def test_sized_zigzag(bitwidth: int, data: bytes, value: int):
    assert SizedZigZag(bitwidth).parse(data) == value
    assert SizedZigZag(bitwidth).build(value) == data


@pytest.mark.parametrize(
    "bitwidth,value",
    [
        (32, 2147483648),
        (32, -2147483649),
        (32, None),
        (64, 9223372036854775808),
        (64, -9223372036854775809),
        (64, "string"),
    ],
)
def test_sized_zigzag_build_errors(bitwidth: int, value: object):
    with pytest.raises(IntegerError):
        assert SizedZigZag(bitwidth).build(value)  # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize(
    "bitwidth,data,exc",
    [
        (32, b"\xff\xff\xff\xff", StreamError),
        (32, b"\xff\xff\xff\xff\x10", IntegerError),
        (64, b"\xff\xff\xff\xff\xff\xff\xff\xff", StreamError),
        (64, b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x02", IntegerError),
    ],
)
def test_sized_zigzag_parse_errors(bitwidth: int, data: object, exc: type[Exception]):
    with pytest.raises(exc):
        assert SizedZigZag(bitwidth).parse(data)  # pyright: ignore[reportArgumentType]
