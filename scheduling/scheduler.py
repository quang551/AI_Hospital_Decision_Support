from scheduling.priority_queue import PriorityQueue


class Scheduler:
    def __init__(self):
        self.queue = PriorityQueue()
        self.schedules = []

    def add_patient(self, patient):
        self.queue.add_patient(patient)

    def create_schedule(self, doctors, rooms, time_slots):
        self.schedules = []

        doctor_index = 0
        room_index = 0
        time_index = 0

        while not self.queue.is_empty():
            patient = self.queue.get_next_patient()

            if not doctors or not rooms or not time_slots:
                break

            doctor = doctors[doctor_index % len(doctors)]
            room = rooms[room_index % len(rooms)]
            time = time_slots[time_index % len(time_slots)]

            schedule = {
                "patient": patient,
                "doctor": doctor,
                "room": room,
                "time": time
            }

            self.schedules.append(schedule)

            doctor_index += 1
            room_index += 1
            time_index += 1

        return self.schedules