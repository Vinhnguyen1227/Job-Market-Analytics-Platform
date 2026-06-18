# Chapter 1: Core Platform & Infrastructure Topology

## 1.1 Overview
The foundation of the CareerIntel platform is a highly resilient, polyglot microservices architecture. Designed to integrate web scraping, full-text search, and real-time user interfaces, the infrastructure relies on Docker Compose to orchestrate seven concurrent containers. This topology ensures that the Next.js frontend, the Elasticsearch search engine, and the core PostgreSQL database operate seamlessly within a secure, internal software-defined network.

## 1.2 Core Platform Topology
The primary user-facing and data management layers of the application are supported by the following containerized services:
- **`next-app`**: The Next.js 16 (App Router) frontend serving both Server-Side Rendered (SSR) web pages and API routes (`port 3000`). It acts as the primary gateway for users interacting with the job search interface and user profiles.
- **`elasticsearch`**: An Elasticsearch 8.13.0 node optimized for complex full-text queries and faceted filtering, essential for querying thousands of normalized job postings.
- **`redis`**: Operates as an in-memory session cache and handles rapid enumerations (e.g., job tracking state), utilizing the `ioredis` library on the Next.js side.
- **`mongodb`**: Provides document-based storage for flexible data schemas, utilized heavily by the Next.js API routes for managing user chat sessions via the `chatService`.

(Note: The core user and job data are persisted in a managed Supabase PostgreSQL instance, which the containerized services access securely via Service Role Keys).

## 1.3 Next.js Production Containerization
The `next-app` service is deployed using a highly optimized, multi-stage Dockerfile designed specifically for Node.js environments.

1. **Stage 1 (deps)**: Utilizes `node:20-alpine` and `npm ci` to cleanly install dependencies, maximizing cache hits during the build process.
2. **Stage 2 (builder)**: Compiles the React application. Telemetry is explicitly disabled (`NEXT_TELEMETRY_DISABLED=1`) to prevent external analytics requests during CI/CD. The build outputs an optimized `.next` standalone directory.
3. **Stage 3 (runner)**: The final production image. It explicitly copies only the necessary compilation artifacts (`package.json`, `node_modules`, `public`, `.next`) from the builder stage. This drastically reduces the final attack surface and image size, establishing a secure environment configured tightly around `NODE_ENV=production`.

## 1.4 Database Health Probing & Startup Sequencing
In a distributed microservices environment, strict boot sequencing is mandatory to prevent cascade failures when upstream dependencies are unresponsive. CareerIntel implements comprehensive database health probing directly within the `docker-compose.yml`.

Services do not blindly depend on container startup; instead, they utilize the `depends_on` configuration coupled with `condition: service_healthy`.
- **Redis Health Check**: The container executes `redis-cli ping` every 10 seconds.
- **MongoDB Health Check**: The container executes `mongosh --eval "db.adminCommand('ping')"` with a robust 20-second start period to account for disk initialization.
- **Elasticsearch Health Check**: A custom shell script polls the `_cluster/health` HTTP endpoint, ensuring the internal state has achieved `green` or `yellow` status before accepting external traffic.

The Next.js and FastAPI application containers are instructed by Docker Compose to halt their startup procedures until these specific health conditions evaluate to true, guaranteeing a robust boot process.

## 1.5 Internal Docker DNS Service Discovery
To eliminate the fragility of hardcoded IP addresses and prevent the accidental exposure of internal databases to the public internet, the architecture leverages Docker's internal DNS resolver.

All containers reside within a default bridge network. Consequently, services map to each other using their logical container names:
- The Next.js API connects to the Redis session store natively via `redis://redis:6379`.
- The internal Elasticsearch sync scripts connect to the cluster via `http://elasticsearch:9200`.

This dynamic service discovery ensures that the backend topology remains secure; only the Next.js frontend (`port 3000`), the Chatbot API (`port 8000`), and Qdrant (`port 6333`) are bound to the host interfaces, while the critical databases remain fully isolated within the Docker subnet.

## 1.6 Elasticsearch Configuration
The Elasticsearch container is explicitly configured for local development and integration within the microservices cluster. It is bootstrapped as a single node (`discovery.type=single-node`), removing the overhead of quorum elections. Furthermore, X-Pack security features are disabled (`xpack.security.enabled=false`) to streamline internal container-to-container communication without the friction of TLS and basic authentication management during the development phase. Finally, JVM memory limits are strictly enforced via environment variables (`ES_JAVA_OPTS=-Xms512m -Xmx512m`) to prevent the Java heap from starving other containers of host RAM.
