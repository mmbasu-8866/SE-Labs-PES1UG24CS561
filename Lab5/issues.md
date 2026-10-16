# Lab 5: Static Analysis Issues

The line numbers below refer to the original `scheduler_system.py` before the
fixes. Findings are ordered by severity first.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shell command built from a file path | Security - High (Bandit B605) | 43 | `os.system("cat " + file)` invokes a shell with a path that may contain shell syntax; it also relies on the Unix-only `cat` command. | Removed shell execution and used `pathlib.Path` file I/O with UTF-8 encoding. |
| Invalid or reversed time slots | Logic bug - Medium | 30-32, 49 | `slot_hours` accepted malformed input and returned `-2` for `14-12`; the demo also passed an integer time slot. | Added strict `HH-HH` validation and rejected invalid ranges before changing scheduler state. |
| Booking conflicts were still accepted | Data integrity - Medium | 12-19 | A duplicate room/time booking was logged but still inserted into reservations, so the system allowed double-booking. | Detect overlapping intervals, record the conflict, and reject the reservation before allocating equipment. |
| Mutable default and module-global state | Reliability / maintainability - Medium (Pylint W0102, W0603) | 5-12 | `equipment_list=[]` could be shared across calls, and `global next_reservation` coupled every booking to module-level state. | Moved state into independent `RoomScheduler` instances and use `None` for optional equipment. |
| Equipment could be over-allocated | Logic bug - Medium | 16-19 | Booking decremented stock without checking that equipment existed or that enough units were available. | Validate each requested count before recording the booking or changing inventory. |
| Cancellation errors were silently swallowed | Reliability - Low (Bandit B110, Pylint W0702, Flake8 E722) | 22-28 | A bare `except` hid missing reservation IDs and other programming errors, making failed cancellations look successful. | Restore equipment only for a real reservation and raise a clear `KeyError` for unknown IDs. |
| File handles and text encoding were unmanaged | Reliability / portability - Low (Pylint W1514, R1732) | 34-43 | Files were opened without `with` blocks or explicit encoding, so closure and cross-platform text behavior were not guaranteed. | Use context managers and explicit UTF-8 encoding for schedule and conflict files. |
| Style and unused variables | Style / maintainability - Low (Flake8 E302, E305, E501, F841) | 11-59 | Missing blank lines, overlong lines, and unused demo variables obscured the actual behavior. | Reformatted the module and removed unused assignments; verified with Flake8. |
