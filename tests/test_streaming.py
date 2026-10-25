
import main

from fastapi.testclient import TestClient


class FakeOllamaResponse:
    def raise_for_status(self):
        pass

    def iter_lines(self, chunk_size=1):
        yield b'{"response":"Hello ","done":false}'
        yield b'{"response":"from AI!","done":false}'
        yield b'{"done":true}'

    def close(self):
        pass


def test_streaming_response(monkeypatch):

    def fake_post(url, **kwargs):
        assert url.endswith("/api/generate")
        assert kwargs["json"]["stream"] is True

        return FakeOllamaResponse()

    monkeypatch.setattr(
        main.requests,
        "post",
        fake_post
    )

    client = TestClient(main.app)

    response = client.post(
        "/generate/stream",
        json={"prompt": "Hello"}
    )

    assert response.status_code == 200
    assert response.text == "Hello from AI!"


def test_streaming_server_unavailable(monkeypatch):

    def fake_post(url, **kwargs):
        raise main.requests.exceptions.ConnectionError(
            "Ollama is unavailable"
        )

    monkeypatch.setattr(
        main.requests,
        "post",
        fake_post
    )

    client = TestClient(main.app)

    response = client.post(
        "/generate/stream",
        json={"prompt": "Hello"}
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Inference server unavailable"
    }

