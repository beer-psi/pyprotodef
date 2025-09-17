import pytest

from protodef.converter.context import ConverterContext
from protodef.datatypes import NATIVE_TYPES


@pytest.fixture
def converter_context():
    ctx = ConverterContext()
    ctx.native_types = NATIVE_TYPES

    return ctx
