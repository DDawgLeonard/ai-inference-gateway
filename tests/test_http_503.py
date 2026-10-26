
import pytest
import main

from fastapi.testclient import TestClient
from queue_manager import InferenceQueue


@pytest.mark.parametrize(
    "endpoint",
    ["/generate", "/generate/stream"]
)
def test_queue_timeout_returns_503(
    monkeypatch, endpoint
):

    # Create an isolated queue for testing
    test_queue = InferenceQueue(
        max_active=1,
        max_waiting=1,
        wait_timeout=0.05
    )

    monkeypatch.setattr(
        main,
        "inference_queue",
        test_queue
    )

    # Occupy the only inference slot
    test_queue.acquire()

    try:
        with TestClient(main.app) as client:
            response = client.post(
                endpoint,
                json={"prompt": "Hello"}
            )

        assert response.status_code == 503

        assert response.json() == {
            "detail": "Inference queue wait timed out"
        }

        # The timed-out request left the queue
        with test_queue.condition:
            assert test_queue.active == 1
            assert len(test_queue.waiting) == 0

    finally:
        test_queue.release()
