# pyright: reportMissingTypeArgument=false, reportUnknownMemberType=false
from typing import TYPE_CHECKING, Any, TypedDict

from construct import Adapter, Construct
from typing_extensions import override

from protodef.converter.context import ConverterContext

if TYPE_CHECKING:
    from construct import Context


class MapperAdapter(Adapter):
    def __init__(self, subcon: "Construct[Any, Any]", mapping: dict[str, object]):
        super().__init__(subcon)

        self.mapping: dict[object, object] = {}
        self.inverse: dict[object, object] = {}

        for k, v in mapping.items():
            if k.startswith("0x"):
                k = int(k, 16)
            elif k.isnumeric():
                k = int(k)
            elif k == "true":
                k = True
            elif k == "false":
                k = False

            self.mapping[k] = v
            self.inverse[v] = k

    @override
    def _decode(self, obj: object, context: "Context", path: str):
        return self.mapping[obj]

    @override
    def _encode(self, obj: object, context: "Context", path: str):
        return self.inverse[obj]


class MapperArguments(TypedDict):
    type: str | tuple[str, object]
    mappings: dict[str, object]


def convert_mapper(ctx: ConverterContext, arg: MapperArguments):
    return MapperAdapter(ctx.convert_type(arg["type"]), arg["mappings"])
