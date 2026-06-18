# Chapter 1: AI Orchestration & ML Pipeline Architecture

## 1.1 Overview
The CareerIntel platform employs a microservices architecture orchestrated via Docker Compose, specifically tuned to handle asynchronous machine learning inference and natural language processing workloads. Within the cluster of seven specialized containers, the architecture isolates the core AI Orchestrator (`chatbot-api`) and the background extraction processor (`celery-worker`), ensuring that heavy tensor computations do not block web-facing API requests.

## 1.2 System Topology for AI Components
The core logic for the AI assistant and the machine learning pipeline is decentralized across multiple interdependent nodes:
- **`chatbot-api`**: Acts as the primary orchestrator. Built using FastAPI running on Uvicorn (`port 8000`), it exposes endpoints for real-time chat and document uploads. It coordinates the routing of requests to the Small Language Model (SLM) Multi-Adapter architecture.
- **`celery-worker`**: An asynchronous worker process utilizing the Celery distributed task queue. It consumes tasks off the `ml` queue, performing heavy data extraction (via PhoBERT NER) and embedding generation (via BGE-M3) in the background.
- **`redis`**: Serves as the message broker for Celery, managing the queue of asynchronous tasks, and operates as an ultra-fast caching layer for conversational state.
- **`mongodb`**: Persists the long-term chat history using the asynchronous Motor driver, ensuring conversational context remains durable across sessions.
- **`qdrant`**: A high-performance vector database that stores multi-vector representations of resumes, crucial for semantic matching and skill-gap analysis.

## 1.3 Container Build Strategies
The AI components are built from a centralized image configuration defined in `backend/chatbot/Dockerfile` to ensure environment consistency between the web server and background workers.

The base image utilizes `python:3.11-slim` to minimize the container footprint while providing the necessary standard libraries. Crucially, the Dockerfile injects system-level dependencies required for Optical Character Recognition (OCR), specifically `tesseract-ocr` and the Vietnamese language pack `tesseract-ocr-vie`, alongside essential shared libraries (`libgl1`, `libglib2.0-0`) required for document processing.

To optimize the container for CPU-bound inference (as the GPU is accessed externally), the PyTorch installation explicitly targets the CPU wheels (`--index-url https://download.pytorch.org/whl/cpu`). This design choice significantly reduces the image size by omitting massive CUDA runtime libraries from the container itself.

## 1.4 Producer-Consumer Volume Mapping (`shared_tmp`)
A critical bottleneck in distributed machine learning pipelines involving large file payloads (such as PDF or DOCX resumes) is the serialization overhead when pushing data through a message broker.

CareerIntel mitigates this by implementing a Producer-Consumer pattern relying on a shared file system, specifically a Docker volume named `shared_tmp` mapped to `/tmp` in both the `chatbot-api` and `celery-worker` containers.
1. The **Producer** (`chatbot-api`) receives a binary file via a multipart POST request and writes it directly to the `/tmp` volume, generating a unique filepath.
2. It then serializes only the metadata (including the filepath string) into a task payload and pushes it to the Redis broker.
3. The **Consumer** (`celery-worker`) pulls the task from Redis, reads the file directly from the identical `shared_tmp` path, and begins extraction via the PyMuPDF library.

This architectural decision entirely bypasses the need to encode megabytes of binary data into Base64 strings for Redis transit, drastically improving pipeline throughput and reducing memory pressure on the broker.

## 1.5 Host GPU Bridge (`host.docker.internal`)
Running multiple Fine-tuned Large Language Models simultaneously requires direct access to high-end GPU hardware. Traditional GPU passthrough into Docker containers (e.g., via Nvidia Container Toolkit) introduces significant configuration complexity and overhead.

Instead, the architecture utilizes a hybrid approach: the Ollama inference engine runs natively on the host machine, while the application logic remains fully containerized. To allow the isolated microservices to communicate with the host's inference engine, Docker Compose injects a custom DNS resolution rule via `extra_hosts: ["host.docker.internal:host-gateway"]`.

This configuration allows the `chatbot-api` and `celery-worker` containers to resolve `http://host.docker.internal:11434`, bypassing the Docker network's default NAT. This effectively bridges the containerized multi-adapter logic with the native, hardware-accelerated tensor computations executing on the host's GPU environment.
