from typing import TypedDict

from construct import Bytes, GreedyBytes, Prefixed
from typing_extensions import NotRequired

from protodef._path import protodef_to_construct_path
from protodef.converter.context import ConverterContext


class BufferArguments(TypedDict):
    countType: NotRequired[str | tuple[str, object]]
    count: NotRequired[str | int]


def convert_buffer(ctx: ConverterContext, arg: BufferArguments):
    count_type = arg.get("countType")
    count = arg.get("count")

    if count_type is None and count is None:
        msg = "either countType or count must be set for an array"
        raise ValueError(msg)

    if count_type is not None and count is not None:
        msg = "only one of countType or count can be set for an array"
        raise ValueError(msg)

    if count_type is not None:
        return Prefixed(ctx.convert_type(count_type), GreedyBytes)

    if count is not None:
        if isinstance(count, int) or count.isnumeric():
            return Bytes(int(count))

        return Bytes(protodef_to_construct_path(count))

    msg = "unreachable"
    raise RuntimeError(msg)
