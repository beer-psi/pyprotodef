import pytest

from protodef.converter.context import ConverterContext
from protodef.datatypes.bitfield import BitfieldItem


@pytest.mark.parametrize(
    "data,value",
    [
        (b"\x00", False),
        (b"\x01", True),
    ],
)
def test_bool(converter_context: ConverterContext, data: bytes, value: bool):
    con = converter_context.convert_type("bool")

    assert con.parse(data) == value
    assert con.build(value) == data


@pytest.mark.parametrize(
    "data,value",
    [
        (b"\x01", 1),
        (b"\x7f", 127),
        (b"\xac\x02", 300),
        (b"\xa0\x8d\x06", 100000),
        (b"\x84\x86\x88\x08", 16909060),
        (b"\xff\xff\xff\xff\x0f", -1),
        (b"\xff\xff\xff\xff\x07", 2147483647),
        (b"\x80\x80\x80\x80\x08", -2147483648),
    ],
)
def test_varint(converter_context: ConverterContext, data: bytes, value: int):
    con = converter_context.convert_type("varint")

    assert con.parse(data) == value
    assert con.build(value) == data


@pytest.mark.parametrize(
    "data,value",
    [
        (b"\x01", 1),
        (b"\x7f", 127),
        (b"\xac\x02", 300),
        (b"\xa0\x8d\x06", 100000),
        (b"\x84\x86\x88\x08", 16909060),
    ],
)
def test_varint64(converter_context: ConverterContext, data: bytes, value: int):
    con = converter_context.convert_type("varint64")

    assert con.parse(data) == value
    assert con.build(value) == data


@pytest.mark.parametrize(
    "data,value",
    [
        (b"\x01", 1),
        (b"\x7f", 127),
        (b"\xac\x02", 300),
        (b"\xa0\x8d\x06", 100000),
        (b"\x84\x86\x88\x08", 16909060),
    ],
)
def test_varint128(converter_context: ConverterContext, data: bytes, value: int):
    con = converter_context.convert_type("varint128")

    assert con.parse(data) == value
    assert con.build(value) == data


@pytest.mark.parametrize(
    "data,value",
    [
        (b"\x02", 1),
    ],
)
def test_zigzag32(converter_context: ConverterContext, data: bytes, value: int):
    con = converter_context.convert_type("zigzag32")

    assert con.parse(data) == value
    assert con.build(value) == data


@pytest.mark.parametrize(
    "data,value",
    [
        (b"\x02", 1),
    ],
)
def test_zigzag64(converter_context: ConverterContext, data: bytes, value: int):
    con = converter_context.convert_type("zigzag64")

    assert con.parse(data) == value
    assert con.build(value) == data


@pytest.mark.parametrize(
    "type,data,value",
    [
        (["buffer", {"count": 3}], b"\x05\x10\xae", b"\x05\x10\xae"),
        (["buffer", {"countType": "u8"}], b"\x03\x05\x10\xae", b"\x05\x10\xae"),
    ],
)
def test_buffer(
    converter_context: ConverterContext, type: object, data: bytes, value: bytes
):
    con = converter_context.convert_type(type)

    assert con.parse(data) == value
    assert con.build(value) == data


@pytest.mark.parametrize(
    "type,data,value",
    [
        (["pstring", {"count": 6}], b"Hello!", "Hello!"),
        (["pstring", {"countType": "i16"}], b"\x00\x06Hello!", "Hello!"),
        (
            ["pstring", {"countType": "i16"}],
            b"\x00\x10\xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf\x21",
            "こんにちは!",
        ),
        (["pstring", {"countType": "varint"}], b"\x06Hello!", "Hello!"),
        (
            ["pstring", {"countType": "varint"}],
            b"\x10\xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf\x21",
            "こんにちは!",
        ),
    ],
)
def test_pstring(
    converter_context: ConverterContext, type: object, data: bytes, value: str
):
    con = converter_context.convert_type(type)

    assert con.parse(data) == value
    assert con.build(value) == data


@pytest.mark.parametrize(
    "data,value",
    [
        (b"Hello!\x00", "Hello!"),
        (
            b"\xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf\x21\x00",
            "こんにちは!",
        ),
    ],
)
def test_cstring(converter_context: ConverterContext, data: bytes, value: str):
    con = converter_context.convert_type("cstring")

    assert con.parse(data) == value
    assert con.build(value) == data


def test_void(converter_context: ConverterContext):
    con = converter_context.convert_type("void")

    assert con.parse(b"") is None
    assert con.build(None) == b""


@pytest.mark.parametrize(
    "type,data,value",
    [
        (
            ["bitfield", [{"name": "one", "size": 8, "signed": False}]],
            b"\xff",
            {"one": 255},
        ),
        (
            ["bitfield", [{"name": "one", "size": 8, "signed": True}]],
            b"\xff",
            {"one": -1},
        ),
        (
            [
                "bitfield",
                [
                    {"name": "one", "size": 8, "signed": True},
                    {"name": "two", "size": 8, "signed": True},
                    {"name": "three", "size": 8, "signed": True},
                ],
            ],
            b"\xff\x80\x12",
            {"one": -1, "two": -128, "three": 18},
        ),
        (
            [
                "bitfield",
                [
                    {"name": "one", "size": 4, "signed": False},
                    {"name": "two", "size": 4, "signed": False},
                    {"name": "three", "size": 4, "signed": False},
                ],
            ],
            b"\xff\x80",
            {"one": 15, "two": 15, "three": 8},
        ),
        (
            [
                "bitfield",
                [
                    {"name": "one", "size": 4, "signed": True},
                    {"name": "two", "size": 4, "signed": True},
                    {"name": "three", "size": 4, "signed": True},
                ],
            ],
            b"\xff\x80",
            {"one": -1, "two": -1, "three": -8},
        ),
        (
            ["bitfield", [{"name": "one", "size": 12, "signed": False}]],
            b"\xff\x80",
            {"one": 4088},
        ),
        (
            [
                "bitfield",
                [
                    {"name": "x", "size": 26, "signed": True},
                    {"name": "y", "size": 12, "signed": True},
                    {"name": "z", "size": 26, "signed": True},
                ],
            ],
            b"\x00\x00\x03\x05\x30\x42\xe0\x65",
            {"x": 12, "y": 332, "z": 4382821},
        ),
    ],
)
def test_bitfield(
    converter_context: ConverterContext,
    type: tuple[str, list[BitfieldItem]],
    data: bytes,
    value: object,
):
    con = converter_context.convert_type(type)

    assert con.parse(data) == value
    assert con.build(value) == data


@pytest.mark.parametrize(
    "type,data,value",
    [
        (
            ["bitflags", {"type": "u8", "flags": ["onGround"]}],
            b"\x01",
            {"_value": 1, "onGround": True},
        ),
        (
            ["bitflags", {"type": "u8", "flags": {"onGround": 1}}],
            b"\x01",
            {"_value": 1, "onGround": True},
        ),
        (
            ["bitflags", {"type": "u8", "big": True, "flags": {"onGround": 1}}],
            b"\x01",
            {"_value": 1, "onGround": True},
        ),
    ],
)
def test_bitflags(
    converter_context: ConverterContext, type: object, data: bytes, value: object
):
    con = converter_context.convert_type(type)

    assert con.parse(data) == value
    assert con.build(value) == data


@pytest.mark.parametrize(
    "type,data,value",
    [
        (
            [
                "mapper",
                {"type": "u8", "mappings": {"0": "zero", "1": "one", "2": "two"}},
            ],
            b"\x00",
            "zero",
        ),
        (
            [
                "mapper",
                {"type": "u8", "mappings": {"0": "zero", "1": "one", "2": "two"}},
            ],
            b"\x02",
            "two",
        ),
    ],
)
def test_mapper(
    converter_context: ConverterContext, type: object, data: bytes, value: object
):
    con = converter_context.convert_type(type)

    assert con.parse(data) == value
    assert con.build(value) == data
