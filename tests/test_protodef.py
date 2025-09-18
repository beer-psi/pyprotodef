import protodef


def test_referencing_other_types_in_namespace():
    proto = protodef.from_definition(
        {
            "namespace": {
                "types": {
                    "packet": [
                        "container",
                        [
                            {
                                "name": "name",
                                "type": [
                                    "mapper",
                                    {
                                        "type": "varint",
                                        "mappings": {
                                            "0x34": "abilities",
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "params",
                                "type": [
                                    "switch",
                                    {
                                        "compareTo": "name",
                                        "fields": {
                                            "abilities": "packet_abilities",
                                        },
                                    },
                                ],
                            },
                        ],
                    ],
                    "packet_abilities": [
                        "container",
                        [
                            {"name": "flags", "type": "i8"},
                            {"name": "flyingSpeed", "type": "f32"},
                            {"name": "walkingSpeed", "type": "f32"},
                        ],
                    ],
                },
            }
        }
    )

    assert proto.namespace.packet.parse(  # pyright: ignore[reportAttributeAccessIssue]
        b"\x34\x00\x3d\x4c\xcc\xcd\x3d\xcc\xcc\xcd"
    ) == {
        "name": "abilities",
        "params": {
            "flags": 0,
            "flyingSpeed": 0.05000000074505806,
            "walkingSpeed": 0.10000000149011612,
        },
    }
