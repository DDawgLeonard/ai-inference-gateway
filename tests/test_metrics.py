
from fastapi.testclient import TestClient
from prometheus_client import REGISTRY

import main


def test_request_metrics():

    labels = {
        "endpoint": "/generate",
        "status": "422"
    }

    def get_count():
        return REGISTRY.get_sample_value(
            "ai_gateway_requests_total",
            labels
        ) or 0.0

    before = get_count()

    with TestClient(main.app) as client:

        # Invalid body: FastAPI should return 422
        response = client.post(
            "/generate",
            json={}
        )

        assert response.status_code == 422

        # Check the Prometheus endpoint
        metrics = client.get("/metrics")

    after = get_count()

    # One HTTP response was recorded
    assert after == before + 1

    # Metrics endpoint is accessible
    assert metrics.status_code == 200

    # Expected metrics exist
    assert "ai_gateway_active_requests" in metrics.text
    assert "ai_gateway_waiting_requests" in metrics.text
    assert "ai_gateway_requests_total" in metrics.text
    assert (
        "ai_gateway_inference_request_duration_seconds"
        in metrics.text
    )
