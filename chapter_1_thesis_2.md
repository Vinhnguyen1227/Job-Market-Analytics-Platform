# Chapter 1: Core Platform & Infrastructure Topology

## 1.1 Overview
The foundation of the CareerIntel platform is a highly resilient, polyglot microservices architecture. Designed to integrate web scraping, full-text search, and real-time user interfaces, the infrastructure relies on Docker Compose to orchestrate seven concurrent containers. This topology ensures that the Next.js frontend, the Elasticsearch search engine, and the core PostgreSQL database operate seamlessly within a secure, internal software-defined network.

This chapter focuses on the four core platform services that underpin the data management and user-facing layers (Next.js, Elasticsearch, Redis, MongoDB). The remaining three services—`chatbot-api`, `celery-worker`, and `qdrant`—form the AI Chatbot subsystem and are documented in the companion thesis (Thesis 1).

## 1.2 Core Platform Topology
The primary user-facing and data management layers of the application are supported by the following containerized services:
- **`next-app`**: The Next.js 16 (App Router) frontend serving both Server-Side Rendered (SSR) web pages and API routes (`port 3000`). It acts as the primary gateway for users interacting with the job search interface and user profiles.
- **`elasticsearch`**: An Elasticsearch 8.13.0 node optimized for complex full-text queries and faceted filtering, essential for querying thousands of normalized job postings.
- **`redis`**: Operates as an in-memory session cache and handles rapid enumerations (e.g., job tracking state), utilizing the `ioredis` library on the Next.js side. The container is configured with **password-based authentication** (`--requirepass`) to prevent unauthorized access, and employs **Append-Only File (AOF) persistence** (`--appendonly yes`) to ensure that cached data survives container restarts by writing every mutation to an append-only log on disk.
- **`mongodb`**: Provides document-based storage for flexible data schemas, utilized heavily by the Next.js API routes for managing user chat sessions via the `chatService`.

(Note: The core user and job data are persisted in a managed Supabase PostgreSQL instance, which the containerized services access securely via Service Role Keys).

```mermaid
graph TB
    subgraph "Host Machine"
        OLLAMA["Ollama (Host GPU)<br/>:11434"]
    end

    subgraph "Docker Compose Network (7 Containers)"
        subgraph "Core Platform (Thesis 2)"
            NEXT["next-app<br/>Next.js 16<br/>:3000"]
            ES["elasticsearch<br/>ES 8.13.0<br/>:9200, :9300"]
            REDIS["redis<br/>Alpine + AOF + Auth<br/>:6379"]
            MONGO["mongodb<br/>Mongo Latest<br/>:27017"]
        end

        subgraph "AI Subsystem (Thesis 1)"
            CHATBOT["chatbot-api<br/>FastAPI<br/>:8000"]
            CELERY["celery-worker<br/>Celery ML Queue"]
            QDRANT["qdrant<br/>Vector DB<br/>:6333"]
        end

        SHARED["shared_tmp<br/>(Volume)"]
    end

    NEXT -->|"depends_on<br/>service_healthy"| REDIS
    NEXT -->|"depends_on<br/>service_healthy"| MONGO
    NEXT -->|"depends_on<br/>service_healthy"| ES
    CHATBOT -->|"depends_on<br/>service_healthy"| REDIS
    CHATBOT -->|"depends_on<br/>service_healthy"| ES
    CHATBOT -->|"depends_on<br/>service_started"| QDRANT
    CELERY -->|"depends_on"| REDIS
    CELERY -->|"depends_on"| QDRANT

    CHATBOT <--> SHARED
    CELERY <--> SHARED
    CHATBOT -->|"host.docker.internal"| OLLAMA
    CELERY -->|"host.docker.internal"| OLLAMA
```

## 1.3 Next.js Production Containerization
The `next-app` service is deployed using a highly optimized, multi-stage Dockerfile (38 lines) designed specifically for Node.js environments.

1. **Stage 1 (deps)**: Utilizes `node:20-alpine` and `npm ci` to cleanly install dependencies, maximizing cache hits during the build process.
2. **Stage 2 (builder)**: Compiles the React application. Telemetry is explicitly disabled (`NEXT_TELEMETRY_DISABLED=1`) to prevent external analytics requests during CI/CD. The build outputs an optimized `.next` standalone directory.
3. **Stage 3 (runner)**: The final production image. It explicitly copies only the five necessary compilation artifacts (`package.json`, `node_modules`, `public`, `.next`, `next.config.js`) from the builder stage. This drastically reduces the final attack surface and image size, establishing a secure environment configured tightly around `NODE_ENV=production`.

## 1.4 Database Health Probing & Startup Sequencing
In a distributed microservices environment, strict boot sequencing is mandatory to prevent cascade failures when upstream dependencies are unresponsive. CareerIntel implements comprehensive database health probing directly within the `docker-compose.yml`.

Services do not blindly depend on container startup; instead, they utilize the `depends_on` configuration coupled with `condition: service_healthy`.

| Service | Health Check Command | Interval | Start Period |
|---------|---------------------|----------|-------------|
| **Redis** | `redis-cli -a ${REDIS_PASSWORD} ping` | 10s | 10s |
| **MongoDB** | `mongosh --eval "db.adminCommand('ping')"` | 15s | 20s |
| **Elasticsearch** | `curl _cluster/health` (status: green/yellow) | 30s | 60s |

The Next.js and FastAPI application containers are instructed by Docker Compose to halt their startup procedures until these specific health conditions evaluate to true, guaranteeing a robust boot process. Notably, the Redis health check includes the authentication password flag (`-a`), verifying not just TCP connectivity but the full authentication layer. MongoDB's generous 20-second start period accommodates disk initialization latency, while Elasticsearch's 60-second start period allows time for JVM warmup and shard allocation.

## 1.5 Internal Docker DNS Service Discovery
To eliminate the fragility of hardcoded IP addresses, the architecture leverages Docker's internal DNS resolver. All containers reside within a default bridge network. Consequently, services map to each other using their logical container names:
- The Next.js API connects to the Redis session store natively via `redis://:${REDIS_PASSWORD}@redis:6379`.
- The internal Elasticsearch sync scripts connect to the cluster via `http://elasticsearch:9200`.
- The Chatbot API connects to MongoDB via `mongodb://${MONGO_USER}:${MONGO_PASS}@mongodb:27017/chatbot?authSource=admin`.

## 1.6 Environment Variable Strategy
The application employs a dual-file environment strategy to separate concerns:
- **`.env.local`**: Contains application-specific secrets (Supabase keys, API tokens) used by the Next.js application both during local development and within the Docker container.
- **`.env.docker`**: Contains Docker-specific infrastructure credentials (Redis password, MongoDB root credentials) referenced by `docker-compose.yml` for service configuration.

This separation ensures that infrastructure credentials are not leaked into the application runtime, and application secrets are not exposed to database containers.

## 1.7 Elasticsearch Configuration
The Elasticsearch container is explicitly configured for local development and integration within the microservices cluster. It is bootstrapped as a single node (`discovery.type=single-node`), removing the overhead of quorum elections. Furthermore, X-Pack security features are disabled (`xpack.security.enabled=false`) to streamline internal container-to-container communication without the friction of TLS and basic authentication management during the development phase. Finally, JVM memory limits are strictly enforced via environment variables (`ES_JAVA_OPTS=-Xms512m -Xmx512m`) to prevent the Java heap from starving other containers of host RAM, capping the Elasticsearch process at 1 GB total (512 MB initial + 512 MB maximum).

## 1.8 Technology Choice: Docker Compose vs Kubernetes

The platform employs Docker Compose for container orchestration rather than Kubernetes (K8s). While Kubernetes offers superior features for production-grade deployments—including automatic horizontal pod autoscaling, self-healing via liveness/readiness probes, rolling updates with zero-downtime deployments, and declarative service mesh routing—its operational complexity introduces significant overhead for a development-phase project of this scale.

| Criteria | Docker Compose | Kubernetes |
|----------|---------------|------------|
| **Configuration complexity** | Single YAML file (145 lines) | Multiple resource manifests (Deployment, Service, ConfigMap, Ingress) |
| **Learning curve** | Minimal — `docker compose up -d` | Requires `kubectl`, Helm charts, namespace management |
| **Startup time** | Seconds | Minutes (cluster bootstrapping, pod scheduling) |
| **Health checks** | Native `healthcheck` directive | Liveness/Readiness probes with finer granularity |
| **Scaling** | Manual (`docker compose scale`) | Automatic HPA based on CPU/memory metrics |
| **Service discovery** | Container name DNS (built-in) | CoreDNS with Service objects |
| **Resource overhead** | ~100 MB for Docker Engine | ~2 GB for control plane (etcd, API server, scheduler) |

Docker Compose provides the ideal balance of simplicity and functionality for a seven-container development topology, while the architecture is designed to be Kubernetes-compatible for future production migration.
