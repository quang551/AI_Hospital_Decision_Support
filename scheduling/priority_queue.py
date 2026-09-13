import heapq


class PriorityQueue:
    PRIORITY_LEVELS = {
        "CRITICAL": 1,
        "HIGH": 2,
        "MEDIUM": 3,
        "LOW": 4
    }

    def __init__(self):
        self._queue = []
        self._counter = 0

    def add_patient(self, patient):
        priority = self.PRIORITY_LEVELS.get(
            patient.priority,
            self.PRIORITY_LEVELS["LOW"]
        )

        heapq.heappush(
            self._queue,
            (priority, self._counter, patient)
        )

        self._counter += 1

    def get_next_patient(self):
        if not self._queue:
            return None

        _, _, patient = heapq.heappop(self._queue)

        return patient

    def is_empty(self):
        return len(self._queue) == 0

    def size(self):
        return len(self._queue)