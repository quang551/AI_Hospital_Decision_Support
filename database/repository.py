import sqlite3

from models.patient import Patient
from models.doctor import Doctor
from models.room import Room
from models.appointment import Appointment


class PatientRepository:
    def __init__(self, db_path="hospital.db"):
        self.db_path = db_path

    def add_patient(self, patient):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO patients (
                id,
                name,
                age,
                symptoms,
                severity,
                emergency,
                waiting_time,
                priority
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient.patient_id,
            patient.name,
            patient.age,
            ",".join(patient.symptoms),
            patient.severity,
            patient.emergency,
            patient.waiting_time,
            patient.priority
        ))

        conn.commit()
        conn.close()

    def get_all_patients(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                age,
                symptoms,
                severity,
                emergency,
                waiting_time,
                priority
            FROM patients
        """)

        rows = cursor.fetchall()
        conn.close()

        patients = []

        for row in rows:
            patient = Patient(
                patient_id=row[0],
                name=row[1],
                age=row[2],
                symptoms=row[3].split(",") if row[3] else [],
                severity=row[4],
                emergency=row[5],
                waiting_time=row[6],
                priority=row[7]
            )

            patients.append(patient)

        return patients


class DoctorRepository:
    def __init__(self, db_path="hospital.db"):
        self.db_path = db_path

    def add_doctor(self, doctor):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO doctors (
                id,
                name,
                specialization
            )
            VALUES (?, ?, ?)
        """, (
            doctor.doctor_id,
            doctor.name,
            doctor.specialization
        ))

        conn.commit()
        conn.close()

    def get_all_doctors(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                specialization
            FROM doctors
        """)

        rows = cursor.fetchall()
        conn.close()

        doctors = []

        for row in rows:
            doctor = Doctor(
                doctor_id=row[0],
                name=row[1],
                specialization=row[2]
            )

            doctors.append(doctor)

        return doctors


class RoomRepository:
    def __init__(self, db_path="hospital.db"):
        self.db_path = db_path

    def add_room(self, room):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO rooms (
                id,
                name,
                department
            )
            VALUES (?, ?, ?)
        """, (
            room.room_id,
            room.name,
            room.department
        ))

        conn.commit()
        conn.close()

    def get_all_rooms(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                department
            FROM rooms
        """)

        rows = cursor.fetchall()
        conn.close()

        rooms = []

        for row in rows:
            room = Room(
                room_id=row[0],
                name=row[1],
                department=row[2]
            )

            rooms.append(room)

        return rooms

class AppointmentRepository:
    def __init__(self, db_path="hospital.db"):
        self.db_path = db_path

    def add_appointment(self, appointment):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO appointments (
                id,
                patient_id,
                doctor_id,
                room_id,
                appointment_time
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            appointment.appointment_id,
            appointment.patient.patient_id,
            appointment.doctor.doctor_id,
            appointment.room.room_id,
            appointment.time
        ))

        conn.commit()
        conn.close()

    def get_all_appointments(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                a.id,
                a.appointment_time,
                p.id,
                p.name,
                p.age,
                p.symptoms,
                p.severity,
                p.emergency,
                p.waiting_time,
                p.priority,
                d.id,
                d.name,
                d.specialization,
                r.id,
                r.name,
                r.department
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN rooms r ON a.room_id = r.id
        """)

        rows = cursor.fetchall()
        conn.close()

        appointments = []

        for row in rows:
            patient = Patient(
                patient_id=row[2],
                name=row[3],
                age=row[4],
                symptoms=row[5].split(",") if row[5] else [],
                severity=row[6],
                emergency=row[7],
                waiting_time=row[8],
                priority=row[9]
            )

            doctor = Doctor(
                doctor_id=row[10],
                name=row[11],
                specialization=row[12]
            )

            room = Room(
                room_id=row[13],
                name=row[14],
                department=row[15]
            )

            appointment = Appointment(
                appointment_id=row[0],
                patient=patient,
                doctor=doctor,
                room=room,
                time=row[1]
            )

            appointments.append(appointment)

        return appointments