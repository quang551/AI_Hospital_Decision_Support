class Room:
    def __init__(
        self,
        room_id,
        name,
        department,
        available_times=None
    ):
        self.room_id = room_id
        self.name = name
        self.department = department
        self.available_times = available_times or []

    def __str__(self):
        return (
            f"Room({self.room_id}, "
            f"{self.name}, "
            f"{self.department})"
        )