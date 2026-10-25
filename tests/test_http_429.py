
import pytest

from fastapi.testclient import TestClient
from main import app
from limiter import reserve_inference_slot


@pytest.mark.parametrize(
    "endpoint",
    ["/generate", "/generate/stream"]
)
def test_http_429(endpoint):

    # Occupy both inference slots
    slot1 = reserve_inference_slot()
    slot2 = reserve_inference_slot()

    try:
        next(slot1)
        next(slot2)

        # Send a request while both slots are busy
        with TestClient(app) as client:
            response = client.post(
                endpoint,
                json={"prompt": "Hello"}
            )

        assert response.status_code == 429

        assert response.json()["detail"] == (
            "Too many concurrent inference requests"
        )

    finally:
        # Always release both slots
        slot1.close()
        slot2.close()
