import json
from fastapi.responses import StreamingResponse
import time
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import Depends
from queue_manager import (
    InferenceQueue,
    QueueFullError,
    QueueTimeoutError
)

app = FastAPI()


# Shared queue for this Gateway process
inference_queue = InferenceQueue(
    max_active=2,
    max_waiting=3,
    wait_timeout=10.0
)


def reserve_queue_slot():
    try:
        inference_queue.acquire()

    except QueueFullError:
        raise HTTPException(
            status_code=429,
            detail="Inference waiting queue is full"
        )

    except QueueTimeoutError:
        raise HTTPException(
            status_code=503,
            detail="Inference queue wait timed out"
        )

    try:
        yield
    finally:
        inference_queue.release()


class PromptRequest(BaseModel):
    prompt: str


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post(
    "/generate",
    dependencies=[Depends(reserve_queue_slot)]
)
def generate(request: PromptRequest):
    try:
        start = time.perf_counter()

        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "qwen3:0.6b",
                "prompt": request.prompt,
                "stream": False,
		"think": False
            },
            timeout=(3, 120)
        )

        response.raise_for_status()

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        data = response.json()

        output_tokens = data.get("eval_count", 0)
        eval_duration_ns = data.get("eval_duration", 0)

        tokens_per_second = (
            round(output_tokens * 1e9 / eval_duration_ns, 2)
            if eval_duration_ns > 0
            else None
        )

        return {
            "response": data["response"],
            "latency_ms": round(latency_ms, 2),
            "output_tokens": output_tokens,
            "tokens_per_second": tokens_per_second,
	     "load_duration_ms": round(
                data.get("load_duration", 0) / 1e6, 2
            ),
            "prompt_eval_duration_ms": round(
                data.get("prompt_eval_duration", 0) / 1e6, 2
            ),
            "ollama_total_ms": round(
                data.get("total_duration", 0) / 1e6, 2
            )

        }

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Inference server timed out"
        )

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Inference server unavailable"
        )



@app.post(
    "/generate/stream",
    dependencies=[Depends(reserve_queue_slot)]
)
def generate_stream(request: PromptRequest):

    try:
        upstream = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "qwen3:0.6b",
                "prompt": request.prompt,
                "stream": True,
                "think": False
            },
            stream=True,
            timeout=(3, 120)
        )

        upstream.raise_for_status()

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Inference server timed out"
        )

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Inference server unavailable"
        )

    except requests.exceptions.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Inference server returned an error"
        )

    def text_chunks():
        try:
            for line in upstream.iter_lines(chunk_size=1):
                if not line:
                    continue

                data = json.loads(line)

                if data.get("done"):
                    break

                chunk = data.get("response", "")

                if chunk:
                    yield chunk
        finally:
            upstream.close()

    return StreamingResponse(
        text_chunks(),
        media_type="text/plain; charset=utf-8"
    )
