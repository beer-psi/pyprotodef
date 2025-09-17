from typing import Any, TypedDict

from construct import Rebuild, len_

from protodef._path import protodef_to_construct_path
from protodef.converter.context import ConverterContext


class CountArguments(TypedDict):
    type: str | tuple[str, object]
    countFor: str


def convert_count(ctx: ConverterContext, arg: CountArguments) -> "Rebuild[Any, Any]":
    return Rebuild(
        ctx.convert_type(arg["type"]),
        len_(protodef_to_construct_path(arg["countFor"])),
    )
