
import time
import threading
import requests

from concurrent.futures import ThreadPoolExecutor

URL = "http://127.0.0.1:8000/generate"

# Synchronize the three clients
barrier = threading.Barrier(3)

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

        return {
            "id": request_id,
            "status": response.status_code,
            "elapsed": round(elapsed, 2)
        }

    except requests.exceptions.RequestException as e:
        return {
            "id": request_id,
            "status": "ERROR",
            "error": str(e)
        }


with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(
        executor.map(send_request, [1, 2, 3])
    )

print("\n--- Concurrency Test Results ---")

for result in results:
    print(result)
