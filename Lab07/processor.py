import math


def validate_height_and_fastpass(rider_spec):
    if not isinstance(rider_spec, str):
        raise TypeError("Rider specification must be a string")

    parts = rider_spec.strip().split(":")
    if len(parts) != 2:
        raise ValueError("Invalid rider specification format")

    height_str = parts[0].strip()
    pass_str = parts[1].strip().upper()
    if not height_str:
        raise ValueError("Height is required")

    try:
        height = int(height_str)
    except ValueError as exc:
        raise ValueError("Height must be an integer") from exc

    if height < 0:
        raise ValueError("Height must be non-negative")

    pass_map = {"YES": True, "NO": False}
    if pass_str not in pass_map:
        raise ValueError("FastPass must be YES or NO")

    has_fastpass = pass_map[pass_str]
    eligible = height >= 120
    status = "FastPass Priority" if has_fastpass else "Standard Entry"
    return f"Height {height}cm: {'Approved' if eligible else 'Denied'} ({status})"


def compute_dispatch_throughput(ride_metric_str):
    if not isinstance(ride_metric_str, str):
        raise TypeError("Ride metric must be a string")

    parts = ride_metric_str.strip().split("/")
    if len(parts) != 2:
        raise ValueError("Invalid ride metric format")

    try:
        riders = float(parts[0])
        cycle_mins = float(parts[1])
    except (TypeError, ValueError) as exc:
        raise ValueError("Ride values must be numeric") from exc

    if not math.isfinite(riders) or not math.isfinite(cycle_mins):
        raise ValueError("Ride values must be finite")
    if riders < 0:
        raise ValueError("Rider count must be non-negative")
    if cycle_mins <= 0:
        raise ValueError("Cycle minutes must be positive")

    rate = riders / cycle_mins
    return round(rate, 2)


def resolve_safety_restraint_code(zone_code):
    if not isinstance(zone_code, str):
        raise TypeError("Zone code must be a string")

    prefix = zone_code.strip().upper()[:3]
    if len(prefix) < 3:
        raise ValueError("Zone code must contain at least 3 letters")

    restraint_types = {
        "CST": "Over-the-Shoulder Harness",
        "WTR": "Lap Bar and Seatbelt",
        "DRP": "Hydraulic Shoulder Vest",
        "WHL": "Manual Safety Bar",
    }
    if prefix not in restraint_types:
        raise ValueError("Unknown ride zone code")
    return restraint_types[prefix]


def main():
    print("==== Running validate_height_and_fastpass ====")
    rider_spec = input("Enter rider spec (Height:FastPass, e.g. 140:YES): ")
    try:
        print(validate_height_and_fastpass(rider_spec))
    except (TypeError, ValueError) as exc:
        print(f"Invalid input: {exc}")

    print("\n==== Running compute_dispatch_throughput ====")
    ride_metric = input("Enter riders/mins (e.g. 48/2.5): ")
    try:
        print("Throughput (riders/min):", compute_dispatch_throughput(ride_metric))
    except (TypeError, ValueError) as exc:
        print(f"Invalid input: {exc}")

    print("\n==== Running resolve_safety_restraint_code ====")
    zone_code = input("Enter ride zone code (e.g. CST_01, WTR_A): ")
    try:
        print("Restraint:", resolve_safety_restraint_code(zone_code))
    except (TypeError, ValueError) as exc:
        print(f"Invalid input: {exc}")


if __name__ == "__main__":
    main()
