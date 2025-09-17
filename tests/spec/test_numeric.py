import pytest

from protodef.converter.context import ConverterContext


@pytest.mark.parametrize(
    "type,data,value",
    [
        ("i8", b"\x3d", 61),
        ("i8", b"\x86", -122),
        ("u8", b"\x3d", 61),
        ("u8", b"\x86", 134),
        ("i16", b"\x30\x87", 12423),
        ("i16", b"\xef\x77", -4233),
        ("u16", b"\x30\x87", 12423),
        ("u16", b"\xef\x77", 61303),
        ("i32", b"\x00\x00\x00\xea", 234),
        ("i32", b"\xff\xff\xfc\x00", -1024),
        ("u32", b"\x00\x00\x00\xea", 234),
        ("u32", b"\xff\xff\xfc\x00", 4294966272),
        ("f32", b"\x47\x05\xc3\x00", 34243),
        ("f32", b"\xc6\x42\x4c\x00", -12435),
        ("f64", b"\x40\xe0\xb8\x60\x00\x00\x00\x00", 34243),
        ("f64", b"\xc0\xc8\x49\x80\x00\x00\x00\x00", -12435),
        ("i64", b"\x00\x00\x00\x00\x00\x00\x00\xff", 255),
        ("i64", b"\x81\x00\x00\x00\x00\x00\x00\x00", -9151314442816847872),
        ("u64", b"\x00\x00\x00\x00\x00\x00\x00\xff", 255),
        ("u64", b"\x7f\x00\x00\x00\x00\x00\x00\x00", 9151314442816847872),
        ("li8", b"\x3d", 61),
        ("li8", b"\x86", -122),
        ("lu8", b"\x3d", 61),
        ("lu8", b"\x86", 134),
        ("li16", b"\x87\x30", 12423),
        ("li16", b"\x77\xef", -4233),
        ("lu16", b"\x87\x30", 12423),
        ("lu16", b"\x77\xef", 61303),
        ("li32", b"\xea\x00\x00\x00", 234),
        ("li32", b"\x00\xfc\xff\xff", -1024),
        ("lu32", b"\xea\x00\x00\x00", 234),
        ("lu32", b"\x00\xfc\xff\xff", 4294966272),
        ("lf32", b"\x00\xc3\x05\x47", 34243),
        ("lf32", b"\x00\x4c\x42\xc6", -12435),
        ("lf64", b"\x00\x00\x00\x00\x60\xb8\xe0\x40", 34243),
        ("lf64", b"\x00\x00\x00\x00\x80\x49\xc8\xc0", -12435),
        ("li64", b"\xff\x00\x00\x00\x00\x00\x00\x00", 255),
        ("li64", b"\x00\x00\x00\x00\x00\x00\x00\x81", -9151314442816847872),
        ("lu64", b"\xff\x00\x00\x00\x00\x00\x00\x00", 255),
        ("lu64", b"\x00\x00\x00\x00\x00\x00\x00\x7f", 9151314442816847872),
    ],
)
def test_numerics(
    converter_context: ConverterContext, type: str, data: bytes, value: int
):
    con = converter_context.convert_type(type)

    assert con.parse(data) == value
    assert con.build(value) == data
