from typing import TYPE_CHECKING, Any, Final

from .array import convert_array
from .bitfield import convert_bitfield
from .bitflags import convert_bitflags
from .buffer import convert_buffer
from .container import convert_container
from .count import convert_count
from .mapper import convert_mapper
from .option import convert_option
from .primitives import NATIVE_PRIMITIVE_TYPES
from .pstring import convert_pstring
from .switch import convert_switch
from .varint import NATIVE_VARINT_TYPES, SizedVarInt, SizedZigZag

if TYPE_CHECKING:
    from protodef.types import ProtodefType

NATIVE_TYPES: Final[dict[str, "ProtodefType[Any, Any]"]] = {  # pyright: ignore[reportAssignmentType]
    "array": convert_array,
    "bitfield": convert_bitfield,
    "bitflags": convert_bitflags,
    "buffer": convert_buffer,
    "container": convert_container,
    "count": convert_count,
    "mapper": convert_mapper,
    "option": convert_option,
    "pstring": convert_pstring,
    "switch": convert_switch,
    **NATIVE_PRIMITIVE_TYPES,
    **NATIVE_VARINT_TYPES,
}

__all__ = (
    "NATIVE_PRIMITIVE_TYPES",
    "NATIVE_TYPES",
    "NATIVE_VARINT_TYPES",
    "SizedVarInt",
    "SizedZigZag",
)
