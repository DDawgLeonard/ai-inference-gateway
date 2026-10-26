
import time
import threading
import requests

from collections import Counter
from concurrent.futures import ThreadPoolExecutor

URL = "http://127.0.0.1:8000/generate"

NUM_REQUESTS = 6

# Start all requests at roughly the same time
barrier = threading.Barrier(NUM_REQUESTS)

payload = {
    "prompt": (
        "Write 80 numbered sentences about "
        "how GPUs accelerate AI workloads."
    )
}


def send_request(request_id):
    barrier.wait()

    start = time.perf_counter()

    try:
        response = requests.post(
            URL,
            json=payload,
            timeout=(3, 180)
        )

        elapsed = time.perf_counter() - start

        result = {
            "id": request_id,
            "status": response.status_code,
            "elapsed": round(elapsed, 2)
        }

        if response.status_code != 200:
            result["detail"] = response.text[:200]

        return result

    except requests.exceptions.RequestException as e:
        return {
            "id": request_id,
            "status": "ERROR",
            "error": str(e)
        }


with ThreadPoolExecutor(
    max_workers=NUM_REQUESTS
) as executor:
    results = list(
        executor.map(
            send_request,
            range(1, NUM_REQUESTS + 1)
        )
    )

print("\n--- Queue Test Results ---")

for result in results:
    print(result)

counts = Counter(
    result["status"] for result in results
)

print("\n--- HTTP Status Summary ---")

for status, count in sorted(
    counts.items(),
    key=lambda item: str(item[0])
):
    print(f"HTTP {status}: {count}")
