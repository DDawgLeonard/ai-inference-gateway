
import pytest

from queue_manager import (
    InferenceQueue,
    QueueFullError,
    QueueTimeoutError
)


def test_queue_full():
    queue = InferenceQueue(
        max_active=1,
        max_waiting=0
    )

    # Occupy the only inference slot
    queue.acquire()

    try:
        # No waiting capacity available
        with pytest.raises(QueueFullError):
            queue.acquire()

    finally:
        queue.release()


def test_queue_timeout():
    queue = InferenceQueue(
        max_active=1,
        max_waiting=1,
        wait_timeout=0.05
    )

    # Occupy the only inference slot
    queue.acquire()

    try:
        # Second request must wait and time out
        with pytest.raises(QueueTimeoutError):
            queue.acquire()

        # Timed-out ticket must be removed
        with queue.condition:
            assert len(queue.waiting) == 0
            assert queue.active == 1

    finally:
        queue.release()

    # Slot should be reusable
    queue.acquire()
    queue.release()


def test_fifo_order():
    import time
    from concurrent.futures import ThreadPoolExecutor

    queue = InferenceQueue(
        max_active=1,
        max_waiting=3,
        wait_timeout=10
    )

    execution_order = []

    # Occupy the only available slot
    queue.acquire()

    def worker(name):
        queue.acquire()
        try:
            execution_order.append(name)
        finally:
            queue.release()

    def wait_until_queued(expected):
        deadline = time.monotonic() + 3

        while time.monotonic() < deadline:
            with queue.condition:
                if len(queue.waiting) == expected:
                    return

            time.sleep(0.01)

        raise AssertionError(
            "Request did not enter the queue"
        )

    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = []

        try:
            for index, name in enumerate(
                ["A", "B", "C"], start=1
            ):
                future = pool.submit(worker, name)
                futures.append(future)

                wait_until_queued(index)
        finally:
            # Free the original slot
            queue.release()

        for future in futures:
            future.result(timeout=10)

    assert execution_order == ["A", "B", "C"]

