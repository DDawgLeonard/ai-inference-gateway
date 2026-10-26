
import time

from collections import deque
from threading import Condition


class QueueFullError(Exception):
    pass


class QueueTimeoutError(Exception):
    pass


class InferenceQueue:
    def __init__(
        self,
        max_active=2,
        max_waiting=3,
        wait_timeout=10.0
    ):
        self.max_active = max_active
        self.max_waiting = max_waiting
        self.wait_timeout = wait_timeout

        self.active = 0
        self.waiting = deque()
        self.condition = Condition()

    def acquire(self):
        with self.condition:

            # Start immediately if capacity is available
            if (
                self.active < self.max_active
                and not self.waiting
            ):
                self.active += 1
                return

            # Reject when the waiting queue is full
            if len(self.waiting) >= self.max_waiting:
                raise QueueFullError()

            # Join FIFO waiting queue
            ticket = object()
            self.waiting.append(ticket)

            deadline = (
                time.monotonic() + self.wait_timeout
            )

            while True:
                first = self.waiting[0] is ticket

                if first and self.active < self.max_active:
                    self.waiting.popleft()
                    self.active += 1
                    self.condition.notify_all()
                    return

                remaining = deadline - time.monotonic()

                if remaining <= 0:
                    self.waiting.remove(ticket)
                    self.condition.notify_all()
                    raise QueueTimeoutError()

                self.condition.wait(timeout=remaining)

    def release(self):
        with self.condition:
            if self.active <= 0:
                raise RuntimeError(
                    "No active inference slot to release"
                )

            self.active -= 1
            self.condition.notify_all()
