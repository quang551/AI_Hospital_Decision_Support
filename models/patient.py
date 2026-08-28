class Patient:
    def __init__(
        self,
        patient_id,
        name,
        age,
        symptoms,
        severity,
        emergency,
        waiting_time=0,
        priority=None
    ):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.symptoms = symptoms
        self.severity = severity
        self.emergency = emergency
        self.waiting_time = waiting_time
        self.priority = priority

    def __str__(self):
        return (
            f"Patient({self.patient_id}, "
            f"{self.name}, "
            f"priority={self.priority})"
        )