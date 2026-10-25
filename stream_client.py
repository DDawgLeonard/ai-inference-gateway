
import time
import requests

URL = "http://127.0.0.1:8000/generate/stream"

payload = {
    "prompt": (
        "Explain how GPUs accelerate AI inference "
        "in 10 sentences."
    )
}

print("AI Response:\n")

start = time.perf_counter()
ttft_ms = None

with requests.post(
    URL,
    json=payload,
    stream=True,
    timeout=(3, 120)
) as response:

    response.raise_for_status()
    response.encoding = "utf-8"

    for chunk in response.iter_content(
        chunk_size=1,
        decode_unicode=True
    ):
        if not chunk:
            continue

        if ttft_ms is None and chunk.strip():
            ttft_ms = (
                time.perf_counter() - start
            ) * 1000

        print(chunk, end="", flush=True)

total_ms = (time.perf_counter() - start) * 1000

print("\n\n--- Performance Metrics ---")
print(f"TTFT (approx): {ttft_ms:.2f} ms"
      if ttft_ms is not None
      else "TTFT: no text received")
print(f"Total Latency: {total_ms:.2f} ms")
