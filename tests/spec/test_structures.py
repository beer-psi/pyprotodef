import pytest

from protodef.converter.context import ConverterContext


@pytest.mark.parametrize(
    "type,data,value",
    [
        (
            [
                "container",
                [
                    {"name": "horizontalPos", "type": "u8"},
                    {"name": "y", "type": "u8"},
                    {"name": "blockId", "type": "varint"},
                ],
            ],
            b"\x38\x19\x05",
            {"horizontalPos": 56, "y": 25, "blockId": 5},
        ),
        (
            [
                "container",
                [
                    {"name": "protocolVersion", "type": "varint"},
                    {
                        "name": "serverHost",
                        "type": ["pstring", {"countType": "varint"}],
                    },
                    {"name": "serverPort", "type": "u16"},
                    {"name": "nextState", "type": "varint"},
                ],
            ],
            b"\x2f\x09\x31\x32\x37\x2e\x30\x2e\x30\x2e\x31\x63\xdd\x01",
            {
                "protocolVersion": 47,
                "serverHost": "127.0.0.1",
                "serverPort": 25565,
                "nextState": 1,
            },
        ),
        (
            [
                "container",
                [
                    {
                        "anon": True,
                        "type": [
                            "bitfield",
                            [
                                {"name": "metadata", "size": 4, "signed": False},
                                {"name": "blockId", "size": 12, "signed": False},
                            ],
                        ],
                    },
                    {"name": "y", "type": "u8"},
                    {
                        "anon": True,
                        "type": [
                            "bitfield",
                            [
                                {"name": "z", "size": 4, "signed": False},
                                {"name": "x", "size": 4, "signed": False},
                            ],
                        ],
                    },
                ],
            ],
            b"\xe3\x26\x04\x61",
            {"metadata": 14, "blockId": 806, "y": 4, "z": 6, "x": 1},
        ),
        (
            [
                "container",
                [
                    {"name": "chunkX", "type": "i32"},
                    {"name": "chunkZ", "type": "i32"},
                    {
                        "name": "recordCount",
                        "type": ["count", {"type": "i16", "countFor": "records"}],
                    },
                    {"name": "dataLength", "type": "i32"},
                    {
                        "name": "records",
                        "type": [
                            "array",
                            {
                                "count": "recordCount",
                                "type": [
                                    "container",
                                    [
                                        {
                                            "anon": True,
                                            "type": [
                                                "bitfield",
                                                [
                                                    {
                                                        "name": "metadata",
                                                        "size": 4,
                                                        "signed": False,
                                                    },
                                                    {
                                                        "name": "blockId",
                                                        "size": 12,
                                                        "signed": False,
                                                    },
                                                ],
                                            ],
                                        },
                                        {"name": "y", "type": "u8"},
                                        {
                                            "anon": True,
                                            "type": [
                                                "bitfield",
                                                [
                                                    {
                                                        "name": "z",
                                                        "size": 4,
                                                        "signed": False,
                                                    },
                                                    {
                                                        "name": "x",
                                                        "size": 4,
                                                        "signed": False,
                                                    },
                                                ],
                                            ],
                                        },
                                    ],
                                ],
                            },
                        ],
                    },
                ],
            ],
            b"\x00\x00\x00\x19\x00\x00\x00\x42\x00\x02\x00\x00\x00\x08\xe3\x26\x04\x61\xd3\x26\x04\x06",
            {
                "chunkX": 25,
                "chunkZ": 66,
                "recordCount": 2,
                "dataLength": 8,
                "records": [
                    {"metadata": 14, "blockId": 806, "y": 4, "z": 6, "x": 1},
                    {"metadata": 13, "blockId": 806, "y": 4, "z": 0, "x": 6},
                ],
            },
        ),
    ],
)
def test_container(
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
                "container",
                [
                    {
                        "name": "number",
                        "type": ["count", {"type": "u8", "countFor": "records"}],
                    },
                    {"name": "diameter", "type": "u8"},
                    {
                        "name": "records",
                        "type": ["array", {"count": "number", "type": "u8"}],
                    },
                ],
            ],
            b"\x02\x05\x01\x02",
            {"number": 2, "diameter": 5, "records": [1, 2]},
        )
    ],
)
def test_count(
    converter_context: ConverterContext, type: object, data: bytes, value: object
):
    con = converter_context.convert_type(type)

    assert con.parse(data) == value
    assert con.build(value) == data


@pytest.mark.parametrize(
    "type,data,value",
    [
        (
            ["array", {"countType": "u16", "type": "u8"}],
            b"\x00\x04\x01\x02\x03\x04",
            [1, 2, 3, 4],
        )
    ],
)
def test_array(
    converter_context: ConverterContext, type: object, data: bytes, value: object
):
    con = converter_context.convert_type(type)

    assert con.parse(data) == value
    assert con.build(value) == data
