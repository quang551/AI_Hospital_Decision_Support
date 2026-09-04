import os
import tempfile
import unittest

from database.database import Database
from database.repository import (
    PatientRepository,
    DoctorRepository,
    RoomRepository,
    AppointmentRepository
)
from models.patient import Patient
from models.doctor import Doctor
from models.room import Room
from models.appointment import Appointment


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(
            suffix=".db",
            delete=False
        )
        self.db_path = self.db_file.name
        self.db_file.close()

        self.db = Database(self.db_path)
        self.db.create_tables()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_tables_created(self):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
        """)

        tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        self.assertIn("patients", tables)
        self.assertIn("doctors", tables)
        self.assertIn("rooms", tables)
        self.assertIn("appointments", tables)

    def test_patient_repository(self):
        repository = PatientRepository(self.db_path)

        patient = Patient(
            "P001",
            "Nguyen Van A",
            65,
            ["chest_pain", "fever"],
            "HIGH",
            "HIGH",
            20,
            "CRITICAL"
        )

        repository.add_patient(patient)

        patients = repository.get_all_patients()

        self.assertEqual(len(patients), 1)
        self.assertEqual(patients[0].patient_id, "P001")
        self.assertEqual(patients[0].name, "Nguyen Van A")
        self.assertEqual(
            patients[0].symptoms,
            ["chest_pain", "fever"]
        )
        self.assertEqual(patients[0].priority, "CRITICAL")

    def test_doctor_repository(self):
        repository = DoctorRepository(self.db_path)

        doctor = Doctor(
            "D001",
            "Dr. Tran Van B",
            "Cardiology"
        )

        repository.add_doctor(doctor)

        doctors = repository.get_all_doctors()

        self.assertEqual(len(doctors), 1)
        self.assertEqual(doctors[0].doctor_id, "D001")
        self.assertEqual(doctors[0].name, "Dr. Tran Van B")
        self.assertEqual(
            doctors[0].specialization,
            "Cardiology"
        )

    def test_room_repository(self):
        repository = RoomRepository(self.db_path)

        room = Room(
            "R001",
            "Room 101",
            "Cardiology"
        )

        repository.add_room(room)

        rooms = repository.get_all_rooms()

        self.assertEqual(len(rooms), 1)
        self.assertEqual(rooms[0].room_id, "R001")
        self.assertEqual(rooms[0].name, "Room 101")
        self.assertEqual(
            rooms[0].department,
            "Cardiology"
        )

    def test_appointment_repository(self):
        patient_repository = PatientRepository(self.db_path)
        doctor_repository = DoctorRepository(self.db_path)
        room_repository = RoomRepository(self.db_path)
        appointment_repository = AppointmentRepository(
            self.db_path
        )

        patient = Patient(
            "P001",
            "Nguyen Van A",
            65,
            ["chest_pain"],
            "HIGH",
            "HIGH",
            20,
            "CRITICAL"
        )

        doctor = Doctor(
            "D001",
            "Dr. Tran Van B",
            "Cardiology"
        )

        room = Room(
            "R001",
            "Room 101",
            "Cardiology"
        )

        patient_repository.add_patient(patient)
        doctor_repository.add_doctor(doctor)
        room_repository.add_room(room)

        appointment = Appointment(
            "A001",
            patient,
            doctor,
            room,
            "2026-09-04 14:00"
        )

        appointment_repository.add_appointment(
            appointment
        )

        appointments = appointment_repository.get_all_appointments()

        self.assertEqual(len(appointments), 1)

        result = appointments[0]

        self.assertEqual(result.appointment_id, "A001")
        self.assertEqual(result.patient.patient_id, "P001")
        self.assertEqual(result.doctor.doctor_id, "D001")
        self.assertEqual(result.room.room_id, "R001")
        self.assertEqual(
            result.time,
            "2026-09-04 14:00"
        )


if __name__ == "__main__":
    unittest.main()