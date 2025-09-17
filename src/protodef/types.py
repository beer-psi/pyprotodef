from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal, TypedDict, TypeVar

if TYPE_CHECKING:
    from typing import TypeAlias

    from construct import BuildTypes, Construct, ParsedType

    from .converter.context import ConverterContext

    ProtodefType: TypeAlias = (
        Construct[ParsedType, BuildTypes]
        | Callable[[ConverterContext, object], Construct[ParsedType, BuildTypes]]
    )

T = TypeVar("T")
Tree = dict[str, "T | Tree[T]"]


class ProtodefDefinition(TypedDict, total=False):
    types: dict[str, Literal["native"] | Any]
