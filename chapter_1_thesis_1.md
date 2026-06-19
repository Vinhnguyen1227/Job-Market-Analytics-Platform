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

## 1.6 Container Topology

The complete Docker Compose topology comprises seven containers organized into three functional tiers: the web tier (Next.js frontend), the AI tier (FastAPI orchestrator and Celery worker), and the data tier (Redis, MongoDB, Elasticsearch, Qdrant). An eighth logical node — the Ollama inference engine — runs natively on the host machine outside Docker's network namespace.

```mermaid
graph TB
    subgraph "Docker Compose Network (bridge)"
        subgraph "Web Tier"
            NEXT["next-app<br/>Next.js 16<br/>:3000"]
        end

        subgraph "AI Tier"
            API["chatbot-api<br/>FastAPI / Uvicorn<br/>:8000"]
            CELERY["celery-worker<br/>Celery -Q ml -c 1"]
        end

        subgraph "Data Tier"
            REDIS["redis<br/>redis:alpine<br/>:6379"]
            MONGO["mongodb<br/>mongo:latest<br/>:27017"]
            ES["elasticsearch<br/>ES 8.13.0<br/>:9200 / :9300"]
            QDRANT["qdrant<br/>qdrant:latest<br/>:6333"]
        end
    end

    HOST["Ollama (Host)<br/>:11434<br/>GPU-accelerated"]

    NEXT -->|"HTTP /api/chat"| API
    API -->|"Task dispatch"| REDIS
    CELERY -->|"Task consume"| REDIS
    API -->|"Session R/W"| REDIS
    API -->|"History R/W"| MONGO
    CELERY -->|"History R/W"| MONGO
    API -->|"Job search"| ES
    API -->|"Resume vectors"| QDRANT
    CELERY -->|"Embed + store"| QDRANT
    API -.->|"host.docker.internal:11434"| HOST
    CELERY -.->|"host.docker.internal:11434"| HOST
```

Each container exposes its service on a deterministic port, enabling both inter-container communication via Docker's internal DNS and external development access via port mapping to the host machine. The dashed lines to the Ollama node represent the host-gateway bridge described in §1.5.

## 1.7 Service Startup and Health Check Architecture

Docker Compose orchestrates the startup sequence through a dependency graph with health-gated conditions. Services in the data tier must pass their health probes before dependent services in the AI and web tiers are permitted to start, preventing connection failures during initialization.

### 1.7.1 Health Check Specifications

Each data-tier service defines a Docker health check that verifies operational readiness beyond mere process liveness:

| Service | Health Check Command | Interval | Timeout | Retries | Start Period |
|---------|---------------------|----------|---------|---------|-------------|
| Redis | `redis-cli -a ${REDIS_PASSWORD} ping` | 10s | 5s | 5 | 10s |
| MongoDB | `mongosh --eval "db.adminCommand('ping')"` | 15s | 10s | 5 | 20s |
| Elasticsearch | `curl -s http://localhost:9200/_cluster/health` (checks for `green` or `yellow` status) | 30s | 10s | 5 | 60s |

The start period parameter is critical: Elasticsearch requires up to 60 seconds to initialize its JVM and load indices, during which health check failures are ignored. Redis, being memory-resident, starts within 10 seconds.

### 1.7.2 Dependency Ordering

The `depends_on` directive enforces a strict startup sequence with two condition levels:

```mermaid
flowchart LR
    REDIS["Redis<br/>(service_healthy)"]
    MONGO["MongoDB<br/>(service_healthy)"]
    ES["Elasticsearch<br/>(service_healthy)"]
    QDRANT["Qdrant<br/>(service_started)"]

    REDIS --> API["chatbot-api"]
    ES --> API
    QDRANT --> API

    REDIS --> NEXT["next-app"]
    MONGO --> NEXT
    ES --> NEXT

    REDIS --> CELERY["celery-worker"]
    QDRANT --> CELERY
```

The distinction between `service_healthy` and `service_started` is deliberate. Redis, MongoDB, and Elasticsearch enforce health-gated starts because the application immediately issues queries upon connection. Qdrant uses the weaker `service_started` condition because the Celery worker lazily initializes its Qdrant client only when the first CV upload arrives, tolerating a brief window where the database is still loading its index into memory.

## 1.8 Service Discovery via Docker DNS

Within the Docker Compose bridge network, containers communicate using Docker's embedded DNS resolver. Each service is resolvable by its Compose service name, eliminating the need for static IP configuration or external service registries.

| Source Container | Target Reference | Purpose |
|-----------------|-----------------|---------|
| `next-app` | `http://chatbot-api:8000` | BFF proxy forwards chat and upload requests |
| `chatbot-api` | `redis://:${REDIS_PASSWORD}@redis:6379/0` | Session cache, task broker, job tracker |
| `chatbot-api` | `mongodb://${USER}:${PASS}@mongodb:27017/chatbot?authSource=admin` | Conversation history persistence |
| `chatbot-api` | `http://elasticsearch:9200` | Full-text job search |
| `chatbot-api` | `http://qdrant:6333` | Resume vector storage and retrieval |
| `chatbot-api` | `http://host.docker.internal:11434` | Ollama SLM inference (host-gateway) |
| `celery-worker` | Same Redis, MongoDB, Qdrant, Ollama URIs | Shared data layer for async tasks |

The `CHATBOT_BACKEND_URL=http://chatbot-api:8000` environment variable injected into the `next-app` container enables the Next.js BFF proxy to route API calls to the FastAPI orchestrator without exposing the backend's internal port to the public network. This architecture ensures that the FastAPI server is only accessible through the Next.js application layer, which enforces authentication and rate limiting before forwarding requests.

## 1.9 Environment Variable Architecture

The system employs a three-layer configuration strategy to manage secrets and service-specific settings across containers:

| Layer | File | Scope | Contents |
|-------|------|-------|----------|
| Docker-specific | `.env.docker` | Infrastructure credentials | `REDIS_PASSWORD`, `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD` |
| Shared secrets | `.env.local` | Application-level API keys | `NEXT_PUBLIC_SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, Gemini API keys |
| Inline overrides | `environment:` block | Per-container URI construction | `REDIS_URL`, `MONGODB_URI`, `ELASTICSEARCH_NODE`, `OLLAMA_HOST`, model names |

The inline `environment:` block in each service definition constructs connection URIs by interpolating credentials from the outer env files. For example, the `chatbot-api` service constructs its Redis URL as `redis://:${REDIS_PASSWORD}@redis:6379/0`, combining the password from `.env.docker` with the Docker DNS hostname `redis`. This pattern ensures that credentials are defined in exactly one place while connection URIs are customized per container's network context.

The adapter model names (`MODEL_TOOL_CALL=careerintel-tool-call`, `MODEL_HR_COACH=careerintel-hr-coach`, `MODEL_STRUCTURED_GEN=careerintel-structured-gen`) are injected as environment variables rather than hardcoded, enabling hot-swapping of fine-tuned adapters during A/B testing without container rebuilds.

## 1.10 Volume Persistence Strategy

The Docker Compose configuration defines five named volumes to ensure data durability across container restarts and recreations:

| Volume | Mount Path | Service | Purpose |
|--------|-----------|---------|---------|
| `redis_data` | `/data` | Redis | AOF persistence file for session data and task queue recovery |
| `mongo_data` | `/data/db` | MongoDB | Database files, journal logs, GridFS chunks |
| `es_data` | `/usr/share/elasticsearch/data` | Elasticsearch | Lucene indices, segment files for full-text job search |
| `qdrant_data` | `/qdrant/storage` | Qdrant | HNSW index and payload storage for resume vectors |
| `shared_tmp` | `/tmp` | chatbot-api, celery-worker | Cross-container file exchange (Producer-Consumer pattern, §1.4) |

The first four volumes implement standard data persistence — their contents represent the system's durable state and survive `docker compose down` / `docker compose up` cycles. The `shared_tmp` volume serves a fundamentally different purpose: it functions as an ephemeral inter-process communication (IPC) channel between the API server and the Celery worker, as described in §1.4.

Redis is configured with append-only file persistence (`redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}`), ensuring that both session data and pending task metadata survive container restarts. This is critical because the JobTracker stores in-flight CV extraction job states in Redis hashes with a one-hour TTL — without AOF persistence, a Redis restart during a long-running extraction task would orphan the job, leaving the frontend polling indefinitely.
