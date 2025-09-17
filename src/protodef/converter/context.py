# pyright: reportImportCycles=false
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from construct import Construct, LazyBound

if TYPE_CHECKING:
    from protodef.types import ProtodefType


class ConverterContext:
    def __init__(self):
        self.native_types: "dict[str, ProtodefType[Any, Any]]" = {}
        self.translated_types: "dict[str, ProtodefType[Any, Any]]" = {}
        self.all_type_names: set[str] = set()

    def convert_type(self, protodef_type: object) -> "Construct[Any, Any]":
        if isinstance(protodef_type, str):
            type_id = protodef_type
            arg = None
        elif isinstance(protodef_type, Sequence):
            if not isinstance(type_id := protodef_type[0], str):
                msg = f"type_id must be a string, got {type_id} of {type(type_id)}"
                raise TypeError(msg)
            arg = protodef_type[1]
        else:
            msg = f"unknown type {protodef_type}"
            raise TypeError(msg)

        typ = self.native_types.get(type_id)

        if typ is None:
            typ = self.translated_types.get(type_id)

        if typ is None:
            if type_id in self.all_type_names:
                return LazyBound(lambda: self.convert_type(protodef_type))

            msg = f"unknown type {type_id}"
            raise ValueError(msg)

        if callable(typ):
            return typ(self, arg)

        return typ
