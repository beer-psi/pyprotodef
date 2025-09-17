from typing import TYPE_CHECKING, Any

from protodef.types import Tree

if TYPE_CHECKING:
    from protodef.types import ProtodefType


class ProtodefProtocol:
    """Container object with dynamic attributes from ProtoDef definitions."""

    def __init__(self):
        self._available_types: set[str] = set()

    @property
    def available_types(self) -> list[str]:
        return sorted(self._available_types)

    def add_type(self, type_id: str, type: "ProtodefType[Any, Any]"):
        if hasattr(self, type_id):
            msg = f"cannot override existing attribute with a type: {type_id}"
            raise ValueError(msg)

        setattr(self, type_id, type)
        self._available_types.add(type_id)

    def add_child_types(self, child_name: str, child_protocol: "ProtodefProtocol"):
        if hasattr(self, child_name):
            msg = f"cannot override existing attribute with child: {child_name}"
            raise ValueError(msg)

        setattr(self, child_name, child_protocol)

        for child_type in child_protocol.available_types:
            self._available_types.add(f"{child_name}.{child_type}")

    def load_from_type_tree(self, tree: "Tree[ProtodefType[Any, Any]]"):
        for k, v in tree.items():
            if isinstance(v, dict):
                self.add_child_types(k, ProtodefProtocol().load_from_type_tree(v))
            else:
                self.add_type(k, v)

        return self
