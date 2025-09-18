import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .converter.context import ConverterContext
from .datatypes import NATIVE_TYPES
from .protocol import ProtodefProtocol
from .types import ProtodefDefinition, Tree

if TYPE_CHECKING:
    from .types import ProtodefType


def from_file(
    protocol_file: str | Path,
    *,
    additional_types: dict[str, "ProtodefType[Any, Any]"] | None = None,
):
    if isinstance(protocol_file, str):
        protocol_file = Path(protocol_file)

    with protocol_file.open("rb") as f:
        return from_definition(
            json.load(f),  # pyright: ignore[reportAny]
            additional_types=additional_types,
        )


def from_definition(
    protocol: Any,
    *,
    additional_types: dict[str, "ProtodefType[Any, Any]"] | None = None,
):
    native_types = NATIVE_TYPES.copy()

    if additional_types is not None:
        native_types.update(additional_types)

    ctx = ConverterContext()
    ctx.native_types = native_types

    # keep a list of all the type names so we can handle forward references
    def _recurse_get_type_names(
        protocol: ProtodefDefinition, ns_parts: list[str] | None = None
    ):
        if ns_parts is None:
            ns_parts = []

        type_names: set[str] = {
            ".".join([*ns_parts, type_id]) for type_id in protocol.get("types", {})
        }

        for namespace, subdata in protocol.items():
            if namespace == "types":
                continue

            type_names.update(_recurse_get_type_names(subdata, [*ns_parts, namespace]))  # pyright: ignore[reportArgumentType]

        return type_names

    ctx.all_type_names = _recurse_get_type_names(protocol)

    def _recurse_load_typetree(
        protocol: ProtodefDefinition, ns_parts: list[str] | None = None
    ):
        if ns_parts is None:
            ns_parts = []

        ctx.current_namespace = ".".join(ns_parts)

        typetree: Tree["ProtodefType[Any, Any]"] = {}
        types = protocol.get("types", {})

        for type_id, definition in types.items():
            full_type_id = ".".join([*ns_parts, type_id])

            if definition == "native":
                if full_type_id not in ctx.native_types:
                    msg = (
                        f"Unknown native type {full_type_id}. If this is intentional, "
                        "please provide an implementation using the "
                        "additional_types kwarg."
                    )
                    raise ValueError(msg)

                typetree[type_id] = native_types[full_type_id]

                continue

            typ = ctx.convert_type(definition)
            ctx.translated_types[full_type_id] = typ
            typetree[type_id] = typ

        for namespace, subdata in protocol.items():
            if namespace == "types":
                continue

            typetree[namespace] = _recurse_load_typetree(
                subdata,  # pyright: ignore[reportArgumentType]
                [*ns_parts, namespace],
            )

        return typetree

    typetree = _recurse_load_typetree(protocol)

    return ProtodefProtocol().load_from_type_tree(typetree)
