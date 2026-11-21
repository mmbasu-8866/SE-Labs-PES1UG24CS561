from hypothesis import given, strategies as st

from processor import (
    compute_dispatch_throughput,
    resolve_safety_restraint_code,
    validate_height_and_fastpass,
)


@given(st.text() | st.none())
def test_validate_height_and_fastpass_unhandled(value):
    validate_height_and_fastpass(value)


@given(st.text() | st.none())
def test_compute_dispatch_throughput_unhandled(value):
    compute_dispatch_throughput(value)


@given(st.text() | st.none())
def test_resolve_safety_restraint_code_unhandled(value):
    resolve_safety_restraint_code(value)
