
from threading import BoundedSemaphore
from fastapi import HTTPException

MAX_CONCURRENT_REQUESTS = 2

inference_slots = BoundedSemaphore(
    value=MAX_CONCURRENT_REQUESTS
)


def reserve_inference_slot():
    acquired = inference_slots.acquire(
        blocking=False
    )

    if not acquired:
        raise HTTPException(
            status_code=429,
            detail="Too many concurrent inference requests"
        )

    try:
        yield
    finally:
        inference_slots.release()
