class Doctor:
    def __init__(
        self,
        doctor_id,
        name,
        specialization,
        available_times=None
    ):
        self.doctor_id = doctor_id
        self.name = name
        self.specialization = specialization
        self.available_times = available_times or []

    def __str__(self):
        return (
            f"Doctor({self.doctor_id}, "
            f"{self.name}, "
            f"{self.specialization})"
        )