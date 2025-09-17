# pyright: reportMissingTypeArgument=false
from typing import TYPE_CHECKING, TypedDict

from construct import Adapter, Construct
from typing_extensions import NotRequired, override

from protodef.converter.context import ConverterContext

if TYPE_CHECKING:
    from construct import Context


class BitflagsAdapter(Adapter):
    def __init__(self, subcon: "Construct[int, int]", flag_masks: dict[str, int]):
        super().__init__(subcon)  # pyright: ignore[reportUnknownMemberType]

        self.flag_masks: dict[str, int] = flag_masks

    @override
    def _encode(self, obj: dict[str, bool], context: "Context", path: str) -> int:
        value = 0

        for k, v in obj.items():
            if not v:
                continue

            if k not in self.flag_masks:
                continue

            mask = self.flag_masks[k]
            value |= mask

        return value

    @override
    def _decode(self, obj: int, context: "Context", path: str) -> dict[str, bool | int]:
        result: dict[str, bool | int] = {"_value": obj}

        for k, v in self.flag_masks.items():
            if k == "_value":
                continue

            result[k] = bool(obj & v)

        return result


class BitflagsArguments(TypedDict):
    type: str | tuple[str, object]
    flags: list[str] | dict[str, int]
    big: NotRequired[bool]
    shift: NotRequired[bool]


def convert_bitflags(ctx: ConverterContext, arg: BitflagsArguments):
    flags = arg["flags"]
    flag_masks: dict[str, int] = {}

    if isinstance(flags, list):
        for i, f in enumerate(flags):
            flag_masks[f] = 1 << i
    elif arg.get("shift", False):
        flag_masks = flags.copy()

        for k in flag_masks:
            flag_masks[k] = 1 << flag_masks[k]
    else:
        flag_masks = flags

    return BitflagsAdapter(ctx.convert_type(arg["type"]), flag_masks)
