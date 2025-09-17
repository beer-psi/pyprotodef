from typing import Any, TypedDict

from construct import BitsInteger, BitStruct, Construct, Padding

from protodef.converter.context import ConverterContext


class BitfieldItem(TypedDict):
    name: str
    size: int
    signed: bool


def convert_bitfield(_ctx: ConverterContext, items: list[BitfieldItem]):
    subcons: "list[Construct[Any, Any]]" = [
        item["name"] / BitsInteger(length=item["size"], signed=item["signed"])
        for item in items
    ]
    total_bits = sum(item["size"] for item in items) if len(items) > 0 else 0

    if total_bits % 8 != 0:
        subcons.append(Padding(total_bits % 8))

    return BitStruct(*subcons)
