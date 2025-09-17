from typing import Any, TypedDict

from construct import Construct, Error, Switch
from typing_extensions import NotRequired

from protodef._path import protodef_to_construct_path
from protodef.converter.context import ConverterContext


class SwitchArguments(TypedDict):
    compareTo: NotRequired[str]
    compareToValue: NotRequired[Any]
    fields: dict[str, str | tuple[str, object]]
    default: NotRequired[str | tuple[str, object]]


def convert_switch(ctx: ConverterContext, arg: SwitchArguments):
    compare_to = arg.get("compareTo")
    fields = arg["fields"]
    default = arg.get("default")

    if compare_to is None:
        msg = "compareTo is not set. compareToValue is not supported."
        raise ValueError(msg)

    sanitized_fields: dict[object, "Construct[Any, Any]"] = {}

    for k, v in fields.items():
        if k.startswith("0x"):
            k = int(k, 16)
        elif k.isnumeric():
            k = int(k)
        elif k == "true":
            k = True
        elif k == "false":
            k = False

        sanitized_fields[k] = ctx.convert_type(v)

    if compare_to.startswith("$"):
        arg_name = compare_to[1:]

        def inner(ctx: ConverterContext, arg: dict[str, object]):
            compare_to = arg.get(arg_name)

            if compare_to is None:
                msg = "compareTo is not set. compareToValue is not supported."
                raise ValueError(msg)

            if not isinstance(compare_to, str):
                msg = f"{arg_name} must be a string, got {compare_to}"
                raise TypeError(msg)

            return Switch(
                protodef_to_construct_path(compare_to),
                sanitized_fields,
                ctx.convert_type(default) if default is not None else Error,
            )

        return inner

    return Switch(
        protodef_to_construct_path(compare_to),
        sanitized_fields,
        ctx.convert_type(default) if default is not None else Error,
    )
