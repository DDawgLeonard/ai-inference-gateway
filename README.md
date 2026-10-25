

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



\## Roadmap



\- \[x] Basic inference gateway

\- \[x] Error and timeout handling

\- \[x] Basic performance metrics

\- \[ ] Streaming inference

\- \[ ] Concurrency control

\- \[ ] Redis rate limiting

\- \[ ] Prometheus and Grafana monitoring

\- \[ ] Docker deployment

\- \[ ] Automated load testing



\## Project Status



Prototype under active development.



