"""Schedule conference rooms and shared equipment."""

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path


INITIAL_EQUIPMENT = {"projector": 2, "microphone": 4, "webcam": 1}


def _parse_time_slot(time_slot: str) -> tuple[int, int]:
    """Return the start and end hours for a valid HH-HH time slot."""
    if not isinstance(time_slot, str):
        raise ValueError("A time slot must be text in HH-HH format.")

    parts = time_slot.split("-")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        raise ValueError("A time slot must be text in HH-HH format.")

    start, end = (int(part) for part in parts)
    if not 0 <= start < end <= 24:
        raise ValueError(
            "A time slot must end after it starts and within 24 hours."
        )
    return start, end


def slot_hours(time_slot: str) -> int:
    """Return the duration of a valid time slot in hours."""
    start, end = _parse_time_slot(time_slot)
    return end - start


@dataclass
class Reservation:
    """A room booking and the equipment assigned to it."""

    room: str
    slot: str
    equipment: list[str]


class RoomScheduler:
    """Manage reservations, equipment inventory, and booking conflicts."""

    def __init__(self) -> None:
        self.reservations: dict[int, Reservation] = {}
        self.equipment_pool = INITIAL_EQUIPMENT.copy()
        self.conflicts: list[str] = []
        self.next_reservation_id = 1

    def schedule_room(
        self,
        room_id: str,
        time_slot: str,
        equipment_list: list[str] | None = None,
    ) -> int:
        """Book a room and reserve equipment, rejecting invalid requests."""
        if not isinstance(room_id, str) or not room_id.strip():
            raise ValueError("A room ID must be a non-empty string.")
        start, end = _parse_time_slot(time_slot)
        if equipment_list is None:
            equipment = []
        elif isinstance(equipment_list, list):
            equipment = equipment_list.copy()
        else:
            raise ValueError("Equipment must be provided as a list of names.")
        if not all(isinstance(item, str) for item in equipment):
            raise ValueError("Equipment must be provided as a list of names.")

        for reservation_id, reservation in self.reservations.items():
            existing_start, existing_end = _parse_time_slot(reservation.slot)
            if (
                reservation.room == room_id
                and start < existing_end
                and existing_start < end
            ):
                message = (
                    f"{room_id} conflicts with reservation {reservation_id} "
                    f"at {reservation.slot}"
                )
                self.conflicts.append(message)
                raise ValueError(message)

        for item, requested_count in Counter(equipment).items():
            available = self.equipment_pool.get(item)
            if available is None:
                raise ValueError(f"Unknown equipment: {item}.")
            if requested_count > available:
                raise ValueError(
                    f"Not enough {item}: requested {requested_count}, "
                    f"available {available}."
                )

        reservation_id = self.next_reservation_id
        self.reservations[reservation_id] = Reservation(
            room=room_id,
            slot=time_slot,
            equipment=equipment,
        )
        for item in equipment:
            self.equipment_pool[item] -= 1
        self.next_reservation_id += 1
        return reservation_id

    def cancel_reservation(self, reservation_id: int) -> None:
        """Cancel a booking and return its equipment to inventory."""
        reservation = self.reservations.pop(reservation_id, None)
        if reservation is None:
            raise KeyError(f"Reservation {reservation_id} does not exist.")
        for item in reservation.equipment:
            self.equipment_pool[item] += 1

    def export_schedule(self, file: str | Path = "schedule.json") -> None:
        """Write all reservations as formatted UTF-8 JSON."""
        schedule = {
            reservation_id: asdict(reservation)
            for reservation_id, reservation in self.reservations.items()
        }
        with Path(file).open("w", encoding="utf-8") as schedule_file:
            json.dump(schedule, schedule_file, indent=2)

    def log_conflicts(self, file: str | Path = "conflicts.log") -> None:
        """Append recorded booking conflicts to a UTF-8 text file."""
        timestamp = datetime.now().isoformat(timespec="seconds")
        with Path(file).open("a", encoding="utf-8") as conflict_file:
            for conflict in self.conflicts:
                conflict_file.write(f"{timestamp} {conflict}\n")


def main() -> None:
    """Run a sample schedule and accept one additional booking."""
    scheduler = RoomScheduler()
    scheduler.schedule_room("Board-1", "09-11")

    try:
        scheduler.schedule_room("Board-1", "09-11")
    except ValueError as error:
        print(f"Booking rejected: {error}")

    huddle_reservation = scheduler.schedule_room("Huddle-3", "14-16")
    huddle_slot = scheduler.reservations[huddle_reservation].slot
    print("Slot length for Huddle-3:", slot_hours(huddle_slot))

    slot = input("Slot for Board-2, like 10-12 (Enter for 10-12): ") or "10-12"
    try:
        scheduler.schedule_room("Board-2", slot, ["projector", "webcam"])
    except ValueError as error:
        print(f"Booking rejected: {error}")

    scheduler.export_schedule()
    scheduler.log_conflicts()
    print("Conflicts logged:", len(scheduler.conflicts))
    print("Equipment left:", scheduler.equipment_pool)
    print("Reservations:", scheduler.reservations)


if __name__ == "__main__":
    main()
