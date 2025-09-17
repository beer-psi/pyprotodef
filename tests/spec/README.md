ProtoDef specification tests from the [ProtoDef repository](https://github.com/ProtoDef-io/ProtoDef/tree/master/test),
converted into native `pytest`.

Currently, 1 test is skipped (2 in pytest due to parameterization):
- `conditional` test "container with a variable", due to lack of support for compile time variables
