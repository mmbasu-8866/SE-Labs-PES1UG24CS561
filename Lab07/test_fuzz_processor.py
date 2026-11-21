from hypothesis import given, settings, strategies as st, Verbosity

from processor import (
    compute_dispatch_throughput,
    resolve_safety_restraint_code,
    validate_height_and_fastpass,
)


@settings(verbosity=Verbosity.normal, max_examples=100)
@given(st.text() | st.none())
def test_validate_height_and_fastpass_no_crash(value):
    try:
        validate_height_and_fastpass(value)
    except (ValueError, KeyError, TypeError, AttributeError, IndexError):
        pass


@settings(verbosity=Verbosity.normal, max_examples=100)
@given(st.text() | st.none())
def test_compute_dispatch_throughput_safe(value):
    try:
        compute_dispatch_throughput(value)
    except (ValueError, ZeroDivisionError, TypeError, AttributeError, IndexError):
        pass


@settings(verbosity=Verbosity.normal, max_examples=100)
@given(st.text() | st.none())
def test_resolve_safety_restraint_code_safe(value):
    try:
        resolve_safety_restraint_code(value)
    except (KeyError, TypeError, AttributeError, IndexError, ValueError):
        pass


@given(
    st.integers(min_value=0, max_value=300),
    st.sampled_from(["YES", "NO", "yes", "no", "Yes", "No"]),
)
def test_validate_height_and_fastpass_valid_specs(height, fastpass):
    result = validate_height_and_fastpass(f"{height}:{fastpass}")
    assert f"Height {height}cm" in result
    assert ("Approved" in result) if height >= 120 else ("Denied" in result)
    assert ("FastPass Priority" in result) if fastpass.upper() == "YES" else ("Standard Entry" in result)


@given(
    st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0.1, max_value=120.0, allow_nan=False, allow_infinity=False),
)
def test_compute_dispatch_throughput_properties(riders, mins):
    result = compute_dispatch_throughput(f"{riders}/{mins}")
    assert result == round(riders / mins, 2)


@given(
    st.sampled_from(["CST", "WTR", "DRP", "WHL"]),
    st.text(alphabet="0123456789_ABCXYZ", min_size=0, max_size=10),
)
def test_resolve_safety_restraint_code_known_prefixes(prefix, suffix):
    result = resolve_safety_restraint_code(f"{prefix}_{suffix}")
    expected = {
        "CST": "Over-the-Shoulder Harness",
        "WTR": "Lap Bar and Seatbelt",
        "DRP": "Hydraulic Shoulder Vest",
        "WHL": "Manual Safety Bar",
    }
    assert result == expected[prefix]
