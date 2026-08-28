class Appointment:
    def __init__(
        self,
        appointment_id,
        patient,
        doctor,
        room,
        time
    ):
        self.appointment_id = appointment_id
        self.patient = patient
        self.doctor = doctor
        self.room = room
        self.time = time

    def __str__(self):
        return (
            f"Appointment({self.appointment_id}: "
            f"{self.patient.name} -> "
            f"{self.doctor.name} -> "
            f"{self.room.name} -> "
            f"{self.time})"
        )