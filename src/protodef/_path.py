from typing import TYPE_CHECKING

from construct import this

if TYPE_CHECKING:
    from typing import Any

    from construct import Path


def protodef_to_construct_path(path: str) -> "Path[Any]":
    path_segments = path.split("/")
    result = this

    for segment in path_segments:
        if segment == "":  # root path e.g. /test
            result = result._root
        elif segment == "..":
            result = result._
        else:
            result = result.__getattr__(segment)

    return result
