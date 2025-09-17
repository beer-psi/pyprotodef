from typing import TypedDict

from construct import PaddedString, PascalString
from typing_extensions import NotRequired

from protodef._path import protodef_to_construct_path
from protodef.converter.context import ConverterContext


class PStringArguments(TypedDict):
    countType: NotRequired[str | tuple[str, object]]
    count: NotRequired[str | int]
    encoding: NotRequired[str]


def convert_pstring(ctx: ConverterContext, arg: PStringArguments):
    count_type = arg.get("countType")
    count = arg.get("count")
    encoding = arg.get("encoding", "utf-8")

    if count_type is None and count is None:
        msg = "either countType or count must be set for an array"
        raise ValueError(msg)

    if count_type is not None and count is not None:
        msg = "only one of countType or count can be set for an array"
        raise ValueError(msg)

    if count_type is not None:
        return PascalString(ctx.convert_type(count_type), encoding)

    if count is not None:
        if isinstance(count, int) or count.isnumeric():
            return PaddedString(int(count), encoding)

        return PaddedString(protodef_to_construct_path(count), encoding)

    msg = "unreachable"
    raise RuntimeError(msg)
