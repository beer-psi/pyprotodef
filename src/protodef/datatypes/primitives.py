from typing import TYPE_CHECKING, Any, Final

from construct import (
    BytesInteger,
    CString,
    Flag,
    Float32b,
    Float32l,
    Float64b,
    Float64l,
    Int8sb,
    Int8sl,
    Int8ub,
    Int8ul,
    Int16sb,
    Int16sl,
    Int16ub,
    Int16ul,
    Int32sb,
    Int32sl,
    Int32ub,
    Int32ul,
    Int64sb,
    Int64sl,
    Int64ub,
    Int64ul,
    Pass,
)

if TYPE_CHECKING:
    from protodef.types import ProtodefType


NATIVE_PRIMITIVE_TYPES: Final[dict[str, "ProtodefType[Any, Any]"]] = {
    "void": Pass,
    "bool": Flag,
    "cstring": lambda ctx, arg: CString(
        "utf-8" if arg is None else str(arg.get("encoding", "utf-8"))  # pyright: ignore[reportUnknownArgumentType, reportAttributeAccessIssue, reportUnknownMemberType]
    ),
    "i8": Int8sb,
    "u8": Int8ub,
    "i16": Int16sb,
    "u16": Int16ub,
    "i32": Int32sb,
    "u32": Int32ub,
    "i64": Int64sb,
    "u64": Int64ub,
    "f32": Float32b,
    "f64": Float64b,
    "li8": Int8sl,
    "lu8": Int8ul,
    "li16": Int16sl,
    "lu16": Int16ul,
    "li32": Int32sl,
    "lu32": Int32ul,
    "li64": Int64sl,
    "lu64": Int64ul,
    "lf32": Float32l,
    "lf64": Float64l,
    "int": lambda ctx, arg: BytesInteger(int(arg["size"]), signed=False),  # pyright: ignore[reportUnknownArgumentType, reportIndexIssue]
    "lint": lambda ctx, arg: BytesInteger(int(arg["size"]), signed=False, swapped=True),  # pyright: ignore[reportUnknownArgumentType, reportIndexIssue]
}
