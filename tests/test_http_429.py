
import pytest
import main

from fastapi.testclient import TestClient
from queue_manager import InferenceQueue


@pytest.mark.parametrize(
    "endpoint",
    ["/generate", "/generate/stream"]
)
def test_queue_full_returns_429(monkeypatch, endpoint):

    # Create an isolated queue for testing
    test_queue = InferenceQueue(
        max_active=2,
        max_waiting=0,
        wait_timeout=0.1
    )

    monkeypatch.setattr(
        main,
        "inference_queue",
        test_queue
    )

    # Occupy both active slots
    test_queue.acquire()
    test_queue.acquire()

    try:
        with TestClient(main.app) as client:
            response = client.post(
                endpoint,
                json={"prompt": "Hello"}
            )

        assert response.status_code == 429

        assert response.json() == {
            "detail": "Inference waiting queue is full"
        }

    finally:
        test_queue.release()
        test_queue.release()
