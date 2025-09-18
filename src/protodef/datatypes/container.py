import re
from functools import reduce
from typing import Any, TypedDict, cast

from construct import (
    BitStruct,
    Bytewise,
    Construct,
    If,
    Pass,
    Renamed,
    Restreamed,
    Struct,
    Switch,
    Transformed,
)
from typing_extensions import NotRequired

from protodef.converter.context import ConverterContext

PATH_SEGMENT_RE = re.compile(r"\['([^']+)'\]")  # worst hack ever


class ContainerItem(TypedDict):
    name: NotRequired[str]
    anon: NotRequired[bool]
    type: str | tuple[str, object]


def convert_container(ctx: ConverterContext, arg: list[ContainerItem]):
    subcons: list["Construct[Any, Any]"] = []

    # `anon` is handled by hoisting all fields from the subcon up into this struct.
    # unfortunately construct dropped support for embedding fields in 2.10, so if
    # we encounter an anon bitfield we have to use a bitstruct.
    # this is some really hacky shit and i don't really like it, but hey we work with
    # what we got
    use_bitstruct = any(
        item["type"][0] == "bitfield" and item.get("anon", False) for item in arg
    )

    for item in arg:
        name = item.get("name")
        anon = item.get("anon") is True

        if not name and not anon:
            msg = "either `name` or `anon` must be set for a container item"
            raise ValueError(msg)

        if name and anon:
            msg = "only one of `name` or `anon` can be set for a container item"
            raise ValueError(msg)

        subcon = ctx.convert_type(item["type"])

        if use_bitstruct:
            # if it's not a bitfield, wrap it in bytewise
            if item["type"][0] != "bitfield":
                subcon = Bytewise(subcon)
            # if it's a bitfield, unwrap it from bitstruct
            else:
                subcon = cast(
                    "Transformed[Any, Any] | Restreamed[Any, Any]", subcon
                ).subcon

        if name:
            subcons.append(name / subcon)
        else:
            if isinstance(subcon, Struct):
                subcons.extend(subcon.subcons)
            elif isinstance(subcon, Switch):
                for case, case_subcon in subcon.cases.items():  # pyright: ignore[reportAny]
                    if isinstance(case_subcon, Struct):
                        subcons.extend(
                            [
                                sc.name / If(subcon.keyfunc == case, sc)  # pyright: ignore[reportAny, reportOperatorIssue, reportUnknownArgumentType, reportArgumentType]
                                for sc in case_subcon.subcons
                            ]
                        )
                    else:
                        subcons.append(
                            case_subcon.name
                            / If(
                                subcon.keyfunc == case,
                                case_subcon.subcon
                                if isinstance(case_subcon, Renamed)
                                else case_subcon,
                            )
                        )

                if subcon.default != Pass:
                    condfunc = reduce(
                        lambda a, b: a and b,
                        [subcon.keyfunc != case for case in subcon.cases],
                    )

                    if isinstance(subcon.default, Struct):
                        subcons.extend(
                            [
                                sc.name / If(condfunc, sc)  # pyright: ignore[reportArgumentType]
                                for sc in subcon.default.subcons
                            ]
                        )
                    else:
                        subcons.append(
                            subcon.default.name
                            / If(
                                condfunc,  # pyright: ignore[reportArgumentType]
                                subcon.default.subcon
                                if isinstance(subcon.default, Renamed)
                                else subcon.default,
                            )
                        )
            else:
                subcons.append(subcon)

    if use_bitstruct:
        return BitStruct(*subcons)

    return Struct(*subcons)
