"""Tests for the conference room and equipment scheduler."""

import json
from pathlib import Path
import tempfile
import unittest

from scheduler_system import RoomScheduler, slot_hours


class RoomSchedulerTests(unittest.TestCase):
    """Verify booking validation and reservation state changes."""

    def setUp(self) -> None:
        self.scheduler = RoomScheduler()

    def test_slot_hours_accepts_valid_slot(self) -> None:
        self.assertEqual(slot_hours("09-11"), 2)

    def test_invalid_time_slots_are_rejected(self) -> None:
        for time_slot in ("14-12", "25-26", "09:00-11:00", 1530):
            with self.subTest(time_slot=time_slot):
                with self.assertRaises(ValueError):
                    slot_hours(time_slot)

    def test_overlapping_booking_is_rejected_without_equipment(self) -> None:
        self.scheduler.schedule_room("Board-1", "09-11")

        with self.assertRaisesRegex(ValueError, "conflicts with reservation"):
            self.scheduler.schedule_room("Board-1", "10-12", ["projector"])

        self.assertEqual(self.scheduler.equipment_pool["projector"], 2)
        self.assertEqual(len(self.scheduler.reservations), 1)
        self.assertEqual(len(self.scheduler.conflicts), 1)

    def test_equipment_shortage_does_not_create_reservation(self) -> None:
        with self.assertRaisesRegex(ValueError, "Not enough microphone"):
            self.scheduler.schedule_room(
                "Board-1", "09-11", ["microphone"] * 5
            )

        self.assertEqual(self.scheduler.equipment_pool["microphone"], 4)
        self.assertFalse(self.scheduler.reservations)

    def test_cancel_restores_equipment_and_reports_unknown_id(self) -> None:
        reservation_id = self.scheduler.schedule_room(
            "Board-1", "09-11", ["projector", "webcam"]
        )
        self.scheduler.cancel_reservation(reservation_id)

        self.assertEqual(self.scheduler.equipment_pool["projector"], 2)
        self.assertEqual(self.scheduler.equipment_pool["webcam"], 1)
        with self.assertRaisesRegex(KeyError, "does not exist"):
            self.scheduler.cancel_reservation(77)

    def test_scheduler_instances_do_not_share_state(self) -> None:
        self.scheduler.schedule_room("Board-1", "09-11")

        another_scheduler = RoomScheduler()
        self.assertFalse(another_scheduler.reservations)
        self.assertEqual(another_scheduler.equipment_pool["projector"], 2)

    def test_schedule_export_and_conflict_log(self) -> None:
        self.scheduler.schedule_room("Board-1", "09-11")
        with self.assertRaises(ValueError):
            self.scheduler.schedule_room("Board-1", "09-11")

        with tempfile.TemporaryDirectory() as temporary_directory:
            schedule_path = Path(temporary_directory) / "schedule.json"
            conflicts_path = Path(temporary_directory) / "conflicts.log"
            self.scheduler.export_schedule(schedule_path)
            self.scheduler.log_conflicts(conflicts_path)

            schedule_data = schedule_path.read_text(encoding="utf-8")
            saved_schedule = json.loads(schedule_data)
            saved_conflicts = conflicts_path.read_text(encoding="utf-8")

        self.assertEqual(saved_schedule["1"]["room"], "Board-1")
        self.assertIn(
            "conflicts with reservation 1",
            saved_conflicts,
        )


if __name__ == "__main__":
    unittest.main()
