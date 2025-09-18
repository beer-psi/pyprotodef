import pytest

from protodef.converter.context import ConverterContext


@pytest.mark.parametrize(
    "data,value",
    [
        (b"\x00\x03", {"action": 0, "result": 3}),
        (b"\x02\xff\xff\xfc\x00", {"action": 2, "result": 4294966272}),
    ],
)
def test_switch_going_to_u8_u16_u32(
    converter_context: ConverterContext, data: bytes, value: object
):
    con = converter_context.convert_type(
        [
            "container",
            [
                {"name": "action", "type": "u8"},
                {
                    "name": "result",
                    "type": (
                        "switch",
                        {
                            "compareTo": "action",
                            "fields": {
                                "0": "u8",
                                "1": "u16",
                                "2": "u32",
                            },
                        },
                    ),
                },
            ],
        ]
    )

    assert con.parse(data) == value
    assert con.build(value) == data


def test_anon_switch_with_default(converter_context: ConverterContext):
    con = converter_context.convert_type(
        [
            "container",
            [
                {"name": "count", "type": "varint"},
                {
                    "anon": True,
                    "type": [
                        "switch",
                        {
                            "compareTo": "count",
                            "fields": {"0": "void"},
                            "default": [
                                "container",
                                [{"name": "id", "type": "varint"}],
                            ],
                        },
                    ],
                },
            ],
        ]
    )

    assert con.parse(b"\x00") == {"count": 0, "id": None}
    assert con.parse(b"\x01\x01") == {"count": 1, "id": 1}


@pytest.mark.skip(reason="we do not support compile-time variables yet")
@pytest.mark.parametrize(
    "data,value",
    [
        (b"\x00\x00\x00\x03", {"color": 3}),
        (b"\x00\x00\x00\x02\x04", {"color": 2, "opacity": 4}),
    ],
)
def test_container_with_a_variable(
    converter_context: ConverterContext, data: bytes, value: object
):
    con = converter_context.convert_type(
        [
            "container",
            [
                {"name": "color", "type": "i32"},
                {
                    "name": "opacity",
                    "type": [
                        "switch",
                        {
                            "compareTo": "color",
                            "fields": {"/colorTransparent": "void"},
                            "default": "u8",
                        },
                    ],
                },
            ],
        ]
    )

    assert con.parse(data) == value
    assert con.build(value) == data


@pytest.mark.parametrize(
    "data,value",
    [
        (b"\x00", None),
        (b"\x01\xef\x77", 61303),
    ],
)
def test_option(converter_context: ConverterContext, data: bytes, value: object):
    con = converter_context.convert_type(["option", "u16"])

    assert con.parse(data) == value
    assert con.build(value) == data
