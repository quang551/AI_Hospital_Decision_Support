from scheduling.priority_queue import PriorityQueue


class Scheduler:
    def __init__(self):
        self.queue = PriorityQueue()
        self.schedules = []

    def add_patient(self, patient):
        self.queue.add_patient(patient)

    def create_schedule(self, doctors, rooms, time_slots):
        self.schedules = []

        if not doctors or not rooms or not time_slots:
            return self.schedules

        # Chia bác sĩ theo nhóm
        emergency_doctors = [
            doctor for doctor in doctors
            if str(doctor.specialization).strip().lower() == "emergency"
        ]

        general_doctors = [
            doctor for doctor in doctors
            if str(doctor.specialization).strip().lower()
            == "general medicine"
        ]

        # Chia phòng theo nhóm
        emergency_rooms = [
            room for room in rooms
            if str(room.department).strip().lower() == "emergency"
        ]

        general_rooms = [
            room for room in rooms
            if str(room.department).strip().lower()
            == "general medicine"
        ]

        emergency_doctor_index = 0
        emergency_room_index = 0

        general_doctor_index = 0
        general_room_index = 0

        time_index = 0

        while not self.queue.is_empty():
            patient = self.queue.get_next_patient()

            priority = str(
                getattr(patient, "priority", "LOW")
            ).strip().upper()

            # CRITICAL và HIGH → Emergency
            if priority in ("CRITICAL", "HIGH"):
                if not emergency_doctors or not emergency_rooms:
                    continue

                doctor = emergency_doctors[
                    emergency_doctor_index % len(emergency_doctors)
                ]

                room = emergency_rooms[
                    emergency_room_index % len(emergency_rooms)
                ]

                emergency_doctor_index += 1
                emergency_room_index += 1

            # MEDIUM và LOW → General Medicine
            else:
                if not general_doctors or not general_rooms:
                    continue

                doctor = general_doctors[
                    general_doctor_index % len(general_doctors)
                ]

                room = general_rooms[
                    general_room_index % len(general_rooms)
                ]

                general_doctor_index += 1
                general_room_index += 1

            time = time_slots[time_index % len(time_slots)]
            time_index += 1

            schedule = {
                "patient": patient,
                "doctor": doctor,
                "room": room,
                "time": time
            }

            self.schedules.append(schedule)

        return self.schedules