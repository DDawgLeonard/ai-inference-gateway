\# AI Inference Gateway



A lightweight AI inference gateway built with FastAPI and Ollama.



The project explores LLM serving, inference latency, performance monitoring, and backend reliability.



\## Architecture



Client

&#x20; |

&#x20; v

FastAPI Gateway (Port 8000)

&#x20; |

&#x20; v

Ollama Inference Server (Port 11434)

&#x20; |

&#x20; v

Qwen3 0.6B



\## Current Features



\- Local LLM inference through Ollama

\- REST API built with FastAPI

\- Health check endpoint

\- HTTP 503 connection error handling

\- HTTP 504 timeout handling

\- Inference latency measurement

\- Token generation speed (Tokens/s)

\- Model loading and prompt processing metrics



\## Tech Stack



\- Python 3.12

\- FastAPI

\- Uvicorn

\- Ollama

\- Qwen3 0.6B

\- Requests



\## Getting Started



\### Prerequisites



\- Python 3.12

\- Ollama installed

\- Qwen3 0.6B model downloaded



Download the model:



&#x20;   ollama pull qwen3:0.6b



\### Installation



Create a virtual environment and install dependencies:



&#x20;   python -m venv .venv

&#x20;   python -m pip install -r requirements.txt



Activate the virtual environment or use its Python executable.



\### Run the Gateway



Ensure the Ollama server is running.



&#x20;   python -m uvicorn main:app --reload



Open:



http://127.0.0.1:8000/docs



\## API Endpoints



GET /health



Check the health of the Gateway process.



POST /generate



Send a prompt to the local LLM.



Example request:



&#x20;   {

&#x20;     "prompt": "Explain AI inference."

&#x20;   }



The response includes generated text and inference performance metrics.




## Roadmap

### Completed
- [x] Basic inference gateway
- [x] Error and timeout handling
- [x] Basic inference performance metrics
- [x] Streaming inference
- [x] Client-side TTFT measurement
- [x] Concurrency control
- [x] FIFO request queue
- [x] Queue timeout and HTTP 429/503 handling
- [x] Automated unit and API testing

HEAD
### Planned
- [ ] Redis-based distributed rate limiting
- [ ] Prometheus metrics collection
- [ ] Grafana monitoring dashboard
- [ ] Docker and Docker Compose deployment
- [ ] Automated load testing and benchmarking
- [ ] Kubernetes deployment

\- \[x] Basic inference gateway

\- \[x] Error and timeout handling

\- \[x] Basic performance metrics

\- \[x] Streaming inference

\- \[x] Concurrency control

\- \[x] Redis rate limiting

\- \[x] Prometheus and Grafana monitoring

\- \[ ] Docker deployment

\- \[ ] Automated load testing
 f34ba5a (feat: add Prometheus metrics and Grafana monitoring)



\## Project Status



Prototype under active development.





\## Streaming Inference



The gateway supports real-time text streaming

through the `/generate/stream` endpoint.



\### Run the Streaming Client



Windows:



&#x20;   .\\.venv\\Scripts\\python.exe stream\_client.py



macOS:



&#x20;   .venv/bin/python stream\_client.py



The client displays generated text incrementally

and measures:



\- Approximate Time to First Token (TTFT)

\- Total response latency



\### Run Automated Tests



&#x20;   python -m pytest -q



The current test suite verifies:



\- Successful streaming response

\- HTTP 503 when the inference server is unavailable



\## Version History



\### v0.2 - Streaming Inference



\- Added streaming API endpoint

\- Added Python streaming client

\- Added client-observed TTFT measurement

\- Added automated API tests



\### v0.1 - Initial Gateway



\- Local inference with Ollama

\- Basic API and health checks

\- Timeout and connection error handling

\- Inference performance metrics





\## v0.3 — Concurrency Control



The gateway implements concurrency protection

using Python's threading.BoundedSemaphore.



\### Features



\- Maximum of 2 concurrent inference requests

\- Shared limit across regular and streaming APIs

\- Immediate HTTP 429 response when capacity is full

\- Automatic slot release after request completion

\- Unit and HTTP-level concurrency tests



\### Load Testing



Run:



&#x20;   python concurrent\_client.py



The script sends 3 concurrent inference requests.



Expected behavior:

\- 2 requests are accepted

\- 1 request receives HTTP 429



\### Current Limitations



\- Concurrency control is process-local

\- No persistent request queue

\- No distributed coordination across workers

\- GPU execution concurrency depends on Ollama



Distributed concurrency control using Redis

is planned for a future release.



## v0.4 — FIFO Request Queue

Implemented a bounded, in-memory inference
request queue for GPU workload management.

### Features

- FIFO request scheduling
- Maximum 2 active inference requests
- Maximum 3 waiting requests
- Configurable queue wait timeout (10 seconds)
- HTTP 429 when the waiting queue is full
- HTTP 503 when queue waiting times out
- Shared queue across regular and streaming endpoints

### Concurrency Test

Run:

    python concurrent_client.py

In one local test with 6 concurrent requests:

| Status | Requests |
|--------|----------|
| HTTP 200 | 3 |
| HTTP 429 | 1 |
| HTTP 503 | 2 |

Results depend on model generation time and load.

### Automated Tests

Run:

    python -m pytest -q

Current result: 10 tests passed.

### Limitations

- Queue state exists only in process memory
- No distributed coordination across workers
- No persistent queue or job recovery
- Client disconnection and cancellation handling
  are not fully implemented
- High-load performance has not been validated

### Next Steps

- Docker containerization
- Prometheus metrics
- Grafana dashboards
- Distributed coordination with Redis



## v0.5 — Observability & Monitoring

The AI Inference Gateway includes an observability
stack built with Prometheus and Grafana.

### Monitoring Features

- HTTP request counters by endpoint and status
- Request rate (RPS)
- P95 inference HTTP latency
- Active inference request gauge
- Waiting queue depth gauge
- HTTP error rate monitoring

### Architecture

FastAPI Gateway
    |
    | GET /metrics
    v
Prometheus
    |
    | PromQL
    v
Grafana Dashboard

### Metrics Endpoint

The gateway exposes Prometheus metrics at:

http://localhost:8000/metrics

### Monitoring Dashboard

The Grafana dashboard includes:

1. Inference Request Rate (RPS)
2. Inference P95 Latency
3. Inference Queue Depth
4. Inference HTTP Error Rate

Dashboard JSON:

grafana/dashboards/ai-inference-gateway-dashboard.json

### Local Development

This version runs the FastAPI gateway on the
host machine while Prometheus and Grafana
run in Docker containers.

Start existing monitoring containers:

    docker start ai-prometheus ai-grafana

Prometheus UI:
http://localhost:9090

Grafana UI:
http://localhost:3000

The gateway and Ollama must also be running.

### Automated Tests

Run:

    python -m pytest -q

Latest local validation: 11 tests passed.

### Limitations

- Metrics currently use a single-process design
- P95 measures gateway HTTP latency, not GPU-only time
- Streaming completion latency is not yet measured
- Dashboard JSON import needs independent validation
- Docker Compose deployment is planned for v0.6







