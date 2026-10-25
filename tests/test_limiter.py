
import pytest

from fastapi import HTTPException
from limiter import reserve_inference_slot


def test_concurrency_limit():

    # Request 1 acquires a slot
    request1 = reserve_inference_slot()
    next(request1)

    # Request 2 acquires a slot
    request2 = reserve_inference_slot()
    next(request2)

    try:
        # Request 3 should be rejected
        request3 = reserve_inference_slot()

        with pytest.raises(HTTPException) as error:
            next(request3)

        assert error.value.status_code == 429

    finally:
        # Release both slots
        request1.close()
        request2.close()

    # A new request can acquire a free slot
    request4 = reserve_inference_slot()

    try:
        next(request4)
    finally:
        request4.close()
