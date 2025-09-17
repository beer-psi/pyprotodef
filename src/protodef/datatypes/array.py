# pyright: reportMissingTypeArgument=false
from typing import IO, TYPE_CHECKING, Any, TypedDict

from construct import (
    Array,
    FocusedSeq,
    ListContainer,
    RangeError,
    Rebuild,
    evaluate,
    len_,
    this,
)
from typing_extensions import NotRequired

from protodef._path import protodef_to_construct_path
from protodef.converter.context import ConverterContext

if TYPE_CHECKING:
    from construct import Context


# a sorta annoying issue with arrays is that the array type's context is the array
# itself which does make sense with construct's model, but protodef doesn't have a
# separate context scope for arrays, so this is the hack we're using
class ArrayWithParentContext(Array):
    def _parse(self, stream: IO[bytes], context: "Context", path: str):
        count: int = evaluate(self.count, context)  # pyright: ignore[reportAny]

        # shamefully import parent context
        context = context.copy()  # pyright: ignore[reportAssignmentType]

        if parent_context := context.get("_"):
            context.update(parent_context)  # pyright: ignore[reportAny]

        if count < 0:
            raise RangeError("invalid count %s" % (count,), path=path)

        discard = self.discard
        obj: "ListContainer[Any]" = ListContainer()

        for i in range(count):
            context._index = i
            e = self.subcon._parsereport(stream, context, path)  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]

            if not discard:
                obj.append(e)

        return obj

    def _build(self, obj: object, stream: IO[bytes], context: "Context", path: str):
        count: int = evaluate(self.count, context)  # pyright: ignore[reportAny]

        if count < 0:
            raise RangeError("invalid count %s" % (count,), path=path)

        if not len(obj) == count:  # pyright: ignore[reportArgumentType]
            raise RangeError(
                "expected %d elements, found %d" % (count, len(obj)),  # pyright: ignore[reportArgumentType]
                path=path,
            )

        # shamefully import parent context
        context = context.copy()  # pyright: ignore[reportAssignmentType]

        if parent_context := context.get("_"):
            context.update(parent_context)  # pyright: ignore[reportAny]

        discard = self.discard
        retlist: "ListContainer[Any]" = ListContainer()

        for i, e in enumerate(obj):  # pyright: ignore[reportArgumentType, reportUnknownVariableType]
            context._index = i
            buildret = self.subcon._build(e, stream, context, path)  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]

            if not discard:
                retlist.append(buildret)

        return retlist


class ArrayArguments(TypedDict):
    type: str | tuple[str, object]
    countType: NotRequired[str]
    count: NotRequired[str | int]


def convert_array(ctx: ConverterContext, arg: ArrayArguments):
    count_type = arg.get("countType")
    count = arg.get("count")

    if count_type is None and count is None:
        msg = "either countType or count must be set for an array"
        raise ValueError(msg)

    if count_type is not None and count is not None:
        msg = "only one of countType or count can be set for an array"
        raise ValueError(msg)

    array_type = ctx.convert_type(arg["type"])

    if count_type is not None:
        return FocusedSeq(
            "items",
            "count" / Rebuild(ctx.convert_type(count_type), len_(this.items)),
            "items" / ArrayWithParentContext(this.count, array_type),  # pyright: ignore[reportUnknownArgumentType]
        )

    if count is not None:
        if isinstance(count, int) or count.isnumeric():
            return ArrayWithParentContext(int(count), array_type)

        return ArrayWithParentContext(protodef_to_construct_path(count), array_type)

    msg = "unreachable"
    raise RuntimeError(msg)
