from construct import Flag, FocusedSeq, If, Rebuild, this

from protodef.converter.context import ConverterContext


def convert_option(ctx: ConverterContext, arg: str | tuple[str, object]):
    return FocusedSeq(
        "value",
        "exists" / Rebuild(Flag, lambda ctx: ctx.value is not None),  # pyright: ignore[reportAny]
        "value" / If(this.exists, ctx.convert_type(arg)),
    )
