# pyright: reportAny=false, reportArgumentType=false, reportAttributeAccessIssue=false, reportMissingTypeArgument=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownVariableType=false
"""
A named binary tag (NBT) parser using ProtoDef and some native Construct methods.

NBT is a tree data structure used by Minecraft to store arbitrary data, consisting
of a series of tags, consisting of a tag ID, a name, and a payload. All numbers are
big-endian.
- Tag ID (i8): defines the type of the payload
- Name length (i16)
- Name: UTF-8 string consisting of the number of bytes given by the length
- Payload
"""

import gzip
import os
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any

from construct import (
    Construct,
    Flag,
    FocusedSeq,
    Int8sb,
    Int16ub,
    LazyBound,
    ListContainer,
    PascalString,
    stream_seek,
    stream_write,
)

import protodef
from protodef.converter.context import ConverterContext

if TYPE_CHECKING:
    from construct import Context

BASE_DIR = Path(__file__).parent


class NBTCompound(Construct):
    """
    An NBT compound tag value. It contains any number of tags and ends with an
    NBT end tag (0x00). The NBT end tag does not have a name and a payload.
    """

    def __init__(self, nbt_type: "Construct[Any, Any]"):
        super().__init__()

        self.nbt_type: "Construct[Any, Any]" = nbt_type
        """The NBT type from the ProtoDef defintion."""

    def _parse(self, stream: IO[bytes], context: "Context", path: str):
        result = ListContainer()

        while True:
            tag = Int8sb._parse(stream, context, path)

            if tag == 0:
                return result

            if tag > 20:
                msg = f"invalid tag type: {tag} > 20"
                raise ValueError(msg)

            _ = stream_seek(stream, -1, os.SEEK_CUR, path)

            result.append(self.nbt_type._parse(stream, context, path))

    def _build(self, obj: object, stream: IO[bytes], context: "Context", path: str):
        if not isinstance(obj, list):
            msg = "NBT compound must be built from a list of NBT tags"
            raise TypeError(msg)

        for tag in obj:
            self.nbt_type._build(tag, stream, context, path)

        stream_write(stream, b"\x00", 1, path)

        return obj


def convert_optional_nbt_type(ctx: ConverterContext, arg: dict[str, str]):
    """
    Converter for the `optionalNbtType` type.

    ```json
    ["optionalNbtType", {"tagType": "nbt"}]
    ```
    """

    inner_type = ctx.convert_type(arg["tagType"])

    return FocusedSeq("value", "exists" / Flag, "value" / inner_type)


# Load the protocol from a JSON file, providing some additional types.
#
# - Since NBT `compound`s are recursive and require some special handling (with
# the single-byte end tag), we implement it in native Python, and then bind the
# ProtoDef NBT type to it. LazyBound ensures that this will be created only
# at parse time, after the protocol has been converted.
# - `nbtTagName` is mapped to a simple Construct.
# - `optionalNbtType` is created using a function. All ProtoDef types with the form
# of `["typeName", { "arg1": 42 }]` is converted using a function, with the first
# argument being the conversion context, and the second argument being the arguments
# passed in from JSON.
#
# Note that Minecraft uses Java's [modified UTF-8] for string encoding - an
# implementation using this should use the correct encoding for tag names and
# string tag decoding.
#
# [modified UTF-8]: https://en.wikipedia.org/wiki/UTF-8#Modified_UTF-8
proto = protodef.from_file(
    BASE_DIR
    / "nbt.json",  # nbt protodef from https://github.com/PrismarineJS/prismarine-nbt
    additional_types={
        "compound": LazyBound(lambda: NBTCompound(proto.nbt)),
        "nbtTagName": PascalString(Int16ub, "utf-8"),
        "optionalNbtType": convert_optional_nbt_type,
    },
)

# Access the NBT type using regular dot notation.
assert isinstance(proto.nbt, Construct)

print(
    proto.nbt.parse(
        gzip.decompress(
            (BASE_DIR / "bigtest.nbt").read_bytes(),
        )
    )
)
