import unittest

from scheduling.priority_queue import PriorityQueue
from scheduling.scheduler import Scheduler
from models.patient import Patient
from models.doctor import Doctor
from models.room import Room


class TestPriorityQueue(unittest.TestCase):

    def create_patient(
        self,
        patient_id,
        name,
        priority
    ):
        return Patient(
            patient_id,
            name,
            30,
            ["fever"],
            "MEDIUM",
            "LOW",
            10,
            priority
        )

    def test_priority_order(self):
        queue = PriorityQueue()

        low = self.create_patient(
            "P001",
            "Patient Low",
            "LOW"
        )

        critical = self.create_patient(
            "P002",
            "Patient Critical",
            "CRITICAL"
        )

        high = self.create_patient(
            "P003",
            "Patient High",
            "HIGH"
        )

        medium = self.create_patient(
            "P004",
            "Patient Medium",
            "MEDIUM"
        )

        queue.add_patient(low)
        queue.add_patient(critical)
        queue.add_patient(high)
        queue.add_patient(medium)

        self.assertEqual(
            queue.get_next_patient().priority,
            "CRITICAL"
        )

        self.assertEqual(
            queue.get_next_patient().priority,
            "HIGH"
        )

        self.assertEqual(
            queue.get_next_patient().priority,
            "MEDIUM"
        )

        self.assertEqual(
            queue.get_next_patient().priority,
            "LOW"
        )

    def test_empty_queue(self):
        queue = PriorityQueue()

        self.assertTrue(queue.is_empty())
        self.assertEqual(queue.size(), 0)
        self.assertIsNone(queue.get_next_patient())


class TestScheduler(unittest.TestCase):

    def create_patient(
        self,
        patient_id,
        name,
        priority
    ):
        return Patient(
            patient_id,
            name,
            30,
            ["fever"],
            "MEDIUM",
            "LOW",
            10,
            priority
        )

    def test_scheduler_priority_order(self):
        scheduler = Scheduler()

        low = self.create_patient(
            "P001",
            "Patient Low",
            "LOW"
        )

        critical = self.create_patient(
            "P002",
            "Patient Critical",
            "CRITICAL"
        )

        high = self.create_patient(
            "P003",
            "Patient High",
            "HIGH"
        )

        scheduler.add_patient(low)
        scheduler.add_patient(critical)
        scheduler.add_patient(high)

        doctors = [
            Doctor(
                "D001",
                "Dr. A",
                "Cardiology"
            )
        ]

        rooms = [
            Room(
                "R001",
                "Room 101",
                "Cardiology"
            )
        ]

        time_slots = [
            "14:00",
            "14:30",
            "15:00"
        ]

        schedules = scheduler.create_schedule(
            doctors,
            rooms,
            time_slots
        )

        self.assertEqual(len(schedules), 3)

        self.assertEqual(
            schedules[0]["patient"].patient_id,
            "P002"
        )

        self.assertEqual(
            schedules[1]["patient"].patient_id,
            "P003"
        )

        self.assertEqual(
            schedules[2]["patient"].patient_id,
            "P001"
        )

    def test_scheduler_empty_resources(self):
        scheduler = Scheduler()

        patient = self.create_patient(
            "P001",
            "Patient A",
            "CRITICAL"
        )

        scheduler.add_patient(patient)

        schedules = scheduler.create_schedule(
            [],
            [],
            []
        )

        self.assertEqual(schedules, [])


if __name__ == "__main__":
    unittest.main()