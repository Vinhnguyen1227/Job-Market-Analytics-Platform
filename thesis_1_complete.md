# UNIVERSITY OF SCIENCE AND TECHNOLOGY OF HANOI
# DEPARTMENT OF INFORMATION AND COMMUNICATION TECHNOLOGY

<br><br><br>

# BACHELOR THESIS

<br>

## Title: Intelligent Job Market Aggregation and Analytics Platform

<br><br><br>

**By: Nguyen Vinh**

<br>

**External Supervisor:** Prof. Dr. Nguyen Van A  
**Internal Supervisor:** Assoc. Prof. Dr. Le Van B  

<br><br><br>

### Hanoi, June 2026

---

## SUPERVISOR CERTIFICATION

To whom it may concern,

I, the undersigned supervisor, certify that the bachelor thesis titled **"Intelligent Job Market Aggregation and Analytics Platform"** submitted by **Mr. Nguyen Vinh** is qualified to be presented before the Internship Jury of the academic year 2025-2026.

Hanoi, June 15, 2026

<br>
Supervisor's Signature: _______________________

---

## ACKNOWLEDGEMENTS

I would like to express my deepest gratitude to all those who made it possible for me to complete this bachelor thesis. Foremost, I want to extend my sincere appreciation to my internal and external supervisors for their invaluable guidance, constant encouragement, and insightful feedback throughout the duration of this research. Their expertise in software engineering and machine learning was crucial in steering this project to success.

I am also highly grateful to the Department of Information and Communication Technology at the University of Science and Technology of Hanoi (USTH) for providing a robust academic foundation and supportive environment.

Finally, I would like to thank my family and friends for their unwavering moral support, patience, and encouragement. This work would not have been possible without the collective support of these individuals.

---

## LIST OF ABBREVIATIONS

| Abbreviation | Expanded Form |
| :--- | :--- |
| **API** | Application Programming Interface |
| **BFF** | Backend-For-Frontend |
| **BullMQ** | Bull Message Queue |
| **CI/CD** | Continuous Integration / Continuous Deployment |
| **CV** | Curriculum Vitae |
| **DPO** | Direct Preference Optimization |
| **ES** | Elasticsearch |
| **GHA** | GitHub Actions |
| **HNSW** | Hierarchical Navigable Small World |
| **JWT** | JSON Web Token |
| **KIE** | Key Information Extraction |
| **LLM** | Large Language Model |
| **LoRA** | Low-Rank Adaptation |
| **ML** | Machine Learning |
| **NER** | Named Entity Recognition |
| **NLP** | Natural Language Processing |
| **OCR** | Optical Character Recognition |
| **QLoRA** | Quantized Low-Rank Adaptation |
| **RAG** | Retrieval-Augmented Generation |
| **RLS** | Row Level Security |
| **SLM** | Small Language Model |
| **SFT** | Supervised Fine-Tuning |
| **SOTA** | State Of The Art |
| **SSR** | Server-Side Rendering |
| **TTL** | Time-To-Live |
| **USTH** | University of Science and Technology of Hanoi |

---

## LIST OF TABLES

- **Table 1**: Summary of Aggregated Job Market Data
- **Table 2**: Search Latency under Varying Concurrent Queries
- **Table 3**: Comparative Performance of Base Model vs. Fine-Tuned Adapters
- **Table 4**: Key Platform System Latency Metrics
- **Table 5**: Feature Comparison with Existing Platforms

---

## LIST OF FIGURES

- **Figure 1**: Three-domain AI subsystem architecture (§3.1)
- **Figure 2**: Container topology of the Docker Compose services (§3.1)
- **Figure 3**: Zero-copy file exchange sequence diagram (§3.1)
- **Figure 4**: Chat request pipeline flowchart (§3.1)
- **Figure 5**: End-to-end CV upload pipeline flowchart (§3.1)
- **Figure 6**: Session lifecycle state diagram (§3.2)
- **Figure 7**: Three-tier session read fallback chain (§3.2)
- **Figure 8**: Conversation state machine flowchart (§3.2)
- **Figure 9**: Resume cross-database data pipeline (§3.2)
- **Figure 10**: Server-client rendering trust boundary (§3.3)
- **Figure 11**: Asynchronous task coordination sequence diagram (§3.3)
- **Figure 12**: Response presentation router (§3.3)
- **Figure 13**: Multi-adapter orchestrator architecture (§3.4)
- **Figure 14**: Intent classification resilience cascade (§3.4)
- **Figure 15**: Tool dispatch strategy pattern (§3.4)
- **Figure 16**: Seven-phase training pipeline overview (§3.5)
- **Figure 17**: Data structuring extraction cascade (§3.5)
- **Figure 18**: Three-layer stacked DPO adapter weights diagram (§3.5)


# ABSTRACT

We present an intelligent, end-to-end Job Market Aggregation and Analytics Platform designed to address the highly fragmented and unstructured nature of the Vietnamese employment market. The platform utilizes automated web scraping pipelines running Playwright and BullMQ to continuously harvest postings from multiple prominent Vietnamese job portals, routing raw text outputs through a customized four-phase Large Language Model (LLM) normalization pipeline powered by Google Gemini API. Structured records are indexed into a high-performance Elasticsearch cluster, enabling sub-100ms full-text search, faceted filtering, and real-time market insights across 6,000+ active job postings. To provide personalized career guidance, we implement a resource-efficient AI chatbot based on a 1.5 billion parameter Small Language Model (SLM), Qwen2.5-1.5B. Using Quantized Low-Rank Adaptation (QLoRA) and Direct Preference Optimization (DPO), we fine-tune three specialized, hot-swappable adapters: a JSON tool caller for intent routing, an empathetic HR coach for CV feedback, and a structured generator for interview matrices. A polyglot persistence architecture utilizing Supabase, Redis, MongoDB, and Qdrant manages user sessions, vector resume embeddings, and conversation logs. Automated evaluation using Gemini-as-a-Judge demonstrates high adapter performance (97.3% schema extraction accuracy, 98.0% tool classification accuracy), matching or exceeding models ten times its size. This research proves the viability of deploying fine-tuned, lightweight SLMs for specialized domestic labor market guidance on commodity hardware, offering valuable data-driven tools for Vietnamese students and professionals.

**Key words:** job market analytics, web scraping, Elasticsearch, small language model, fine-tuning, Vietnam labor market.


# I/ INTRODUCTION

## 1.1 Global Context & Motivation

In recent years, the rapid growth of the digital economy has transformed the global and domestic labor markets. Vietnam, as a fast-emerging market, has experienced a significant surge in demand for high-skilled labor, particularly in information technology, digital marketing, and financial services [12]. However, the domestic job market remains highly fragmented. Job postings are scattered across dozens of disconnected online employment portals (such as TopCV, VietnamWorks, and JobOKO), each using proprietary classifications, diverse salary formatting, and varying descriptions. This fragmentation creates search friction for job seekers who must manually browse multiple websites, compile matching data, and evaluate their own qualifications against inconsistent requirement definitions.

For students and young professionals entering this dynamic landscape, the challenge is twofold. First, they lack centralized, real-time analytics to understand broader market demands—such as which skills are most sought after, how salaries are distributed across regions, or which sectors are expanding. Second, they lack access to personalized, expert career guidance. Traditional career consulting is either prohibitively expensive or generic, while existing automated resume screening tools (often based on basic keyword matching) fail to provide actionable, constructive feedback for candidates to improve their resumes and bridge skill gaps.

This research is motivated by the potential of combining web automation, information retrieval, and modern artificial intelligence to build a unified, intelligent analytics platform. By combining automated data aggregation with local large language model (LLM) inference, we can create a system that not only indexes and visualizes market trends in real time but also serves as an interactive, resume-aware career assistant. Such a platform democratizes career guidance, helping candidates optimize their market readiness.

---

## 1.2 Literature Review

### 1.2.1 Web Scraping and Data Normalization in HR Tech
Web scraping is a standard method for aggregating employment data in research and industry. Traditional crawlers rely on libraries like BeautifulSoup or Scrapy. However, modern job portals increasingly utilize Single Page Application (SPA) architectures and anti-bot defenses (such as dynamic DOM rendering, rate limits, and browser fingerprinting). This has shifted the state-of-the-art toward automated browser frameworks like Playwright [10] and Puppeteer, which run headless Chromium instances to simulate human interactions. Task orchestration is typically managed through distributed message queues such as BullMQ [11], which coordinate concurrent scraping workers with rate-limited job scheduling. 

Once scraped, the raw text remains unstructured and noisy. Early normalization techniques relied on rule-based regular expressions and tf-idf vector comparisons to clean salary formats or categorize locations. While fast, these techniques are fragile and fail on semantic variations (e.g., classifying "10-15 triệu" versus "10m-15m VND"). The current paradigm leverages Large Language Models (LLMs) via API services (such as OpenAI's GPT or Google's Gemini [3]) to perform zero-shot and few-shot Named Entity Recognition (NER) and JSON schema extraction, yielding highly structured, clean datasets from messy web sources. For Vietnamese text processing, pre-trained language models such as PhoBERT [8] enable domain-specific NER on Vietnamese documents, extracting named entities (persons, organizations, locations) that rule-based approaches miss. Server-side orchestration of these ML pipelines is increasingly handled by high-performance Python API frameworks such as FastAPI [16].

### 1.2.2 Full-Text Search and Vector Retrieval
To navigate large-scale job databases, efficient search engines are required. Lucene-based search clusters, notably Elasticsearch, serve as the standard for full-text search [2]. They support multi-field querying, BM25 text relevance scoring, and faceted filter aggregations, enabling sub-second search times across millions of records. 

However, keyword search is limited by semantic vocabulary mismatch (e.g., searching "Frontend" might miss "React developer"). This has led to the adoption of vector-based similarity search using dense embeddings (e.g., BGE-M3, Sentence-BERT) indexed in specialized vector databases like Qdrant, following the Retrieval-Augmented Generation (RAG) paradigm [6]. By encoding resumes and job descriptions as high-dimensional vectors, platforms can perform aspect-scoped semantic matching and skill-gap calculations, capturing semantic relationships that keyword matching misses.

### 1.2.3 Parameter-Efficient Fine-Tuning (PEFT) and SLMs
Although giant LLMs (e.g., GPT-4, Llama-3-70B) demonstrate impressive capabilities, deploying them in production presents severe challenges. They require costly, high-end cloud GPU infrastructure, introduce data privacy concerns, and exhibit high latency. Consequently, there is growing academic interest in Small Language Models (SLMs) with under 3 billion parameters, such as Qwen2.5-1.5B [7] or Gemma-2B, which can run locally on consumer-grade hardware.

To match the task performance of larger models, SLMs are adapted using Parameter-Efficient Fine-Tuning (PEFT) techniques, particularly Low-Rank Adaptation (LoRA) and its quantized variant, QLoRA [4]. QLoRA quantizes the base model's weights into 4-bit representation to minimize memory footprint, injecting lightweight trainable low-rank adapters. Direct Preference Optimization (DPO) further aligns model outputs with specific human guidelines (such as consulting tone and formatting constraints) by optimizing directly on pairwise preferences, bypassing the complexity of reinforcement learning with human feedback (RLHF) [9].

---

## 1.3 Problem Statement

Despite these advancements, existing Vietnamese career portals and recruitment tools exhibit three main technical limitations:

1. **Fragmented and Unstructured Data Sources**: Web-scraped data from Vietnamese job sites is extremely noisy, with unstructured salary ranges, non-standardized skill names, and duplicate postings [15]. Standard classification algorithms fail on Vietnamese text due to complex syntax, spelling variations, and mixing of English and Vietnamese technical terms.
2. **High Resource Demands for Intelligent Chatbots**: Deploying interactive, conversational career agents usually requires querying expensive, external cloud APIs or hosting massive models. This is financially unsustainable for domestic institutions and poses privacy risks when processing personal Curriculum Vitae (CV) documents.
3. **Task Drift in Single-Prompt SLMs**: When a tiny model (under 2B parameters) is prompted to handle multiple complex tasks (such as intent classification, resume coaching, and interview generation) in a single configuration, it experiences severe performance degradation, structural output failures, and loss of conversational tone.

---

## 1.4 Research Questions

To address these limitations, this thesis investigates the following key research questions:

1. **RQ1**: How can we design an automated data collection and processing pipeline that crawls, cleans, and normalizes unstructured Vietnamese job postings into a high-quality standardized schema using LLM-in-the-loop techniques?
2. **RQ2**: How can we design a polyglot persistence and retrieval architecture that enables both sub-second full-text job search and aspect-specific vector-based resume matching?
3. **RQ3**: How can we build a resource-efficient, local conversational agent using a multi-adapter SLM architecture that matches the performance of larger models while running on commodity hardware?


# II/ OBJECTIVES

The primary objective of this research is to design, implement, and evaluate an intelligent, end-to-end Job Market Aggregation and Analytics Platform that automates the collection and standardization of Vietnamese job listings, combines high-performance full-text search with real-time market analytics, and deploys a local, privacy-preserving AI career assistant powered by a multi-adapter Small Language Model (SLM). To achieve this, we propose a modular architecture comprising automated multi-source web scraping [10,11], LLM-driven data normalization [3], sub-100ms Elasticsearch retrieval [2], and three task-specific QLoRA adapters [4,5] on a shared Qwen2.5-1.5B base model [7], orchestrated within a containerized polyglot persistence infrastructure [13,14].


# III/ MATERIALS AND METHODS


## 3.1 AI Orchestration & ML Pipeline Architecture

### 3.1.1 Overview

The CareerIntel platform is built around a central architectural premise: a small language model (SLM) with only 1.5 billion parameters can match or exceed the task-specific performance of models ten times its size — provided that its responsibilities are decomposed into discrete, fine-tuned sub-tasks rather than handled by a single general-purpose prompt. This premise drives every layer of the system, from the three-adapter inference engine that serves users in real time, to the six-phase training pipeline that produces those adapters, to the polyglot persistence layer that maintains conversational state across sessions.

This chapter presents the high-level architecture of the AI components: the computational domains that organize the system, the container topology that isolates them, the key design tradeoffs that shape their interaction, and the end-to-end data flows that connect a user's request to an AI-generated response. Subsequent chapters elaborate each domain in depth — Chapter 3 details the persistence layer, Chapter 7 describes the multi-adapter inference engine, and Chapter 8 documents the training pipeline.

### 3.1.2 Three-Domain Architecture

The AI subsystem is organized into three computational domains, each with distinct latency requirements, resource profiles, and failure characteristics. This separation ensures that heavy tensor computations do not block real-time user interactions, and that persistent state remains durable independently of the compute layer's lifecycle.

#### 3.1.2.1 Synchronous Inference Domain

The synchronous inference domain handles the real-time chat loop: receiving a user message, classifying intent, routing to the appropriate adapter, generating a response, and returning it — all within the latency budget of a single HTTP request-response cycle. Two components collaborate in this domain:

- **FastAPI Orchestrator** — the central coordinator that exposes chat and upload endpoints, manages session state, and implements the tool dispatch decision tree. It determines *which* adapter should handle each request and *how* the response should be framed, but delegates the actual text generation to the inference engine.
- **Ollama Inference Engine** — hosts three QLoRA-finetuned adapters on the same Qwen2.5:1.5B base model, each specialized for a different output modality: structured JSON for intent classification (Adapter A), empathetic Vietnamese prose for career coaching (Adapter B), and formatted markdown tables for interview preparation (Adapter C). All three adapters share the base model's weights in memory, with only lightweight LoRA delta matrices differentiating them.

The critical design decision in this domain is that Ollama runs natively on the host machine rather than inside a container. This hybrid approach allows the inference engine to access host GPU hardware directly, avoiding the configuration complexity of Docker GPU passthrough while keeping all application logic fully containerized.

#### 3.1.2.2 Asynchronous Extraction Domain

CV processing — parsing PDFs, running Named Entity Recognition, computing vector embeddings — routinely takes 30 to 180 seconds, far exceeding acceptable synchronous response times. The asynchronous domain isolates these heavy workloads behind a task queue:

- **Celery Worker** — a background processor that consumes extraction tasks from a Redis-backed message queue. It executes the same three-stage extraction cascade used in the training pipeline (semantic chunking → regex extraction → PhoBERT NER), followed by quality scoring and BGE-M3 embedding generation. Machine learning models are pre-warmed at worker startup, eliminating the approximately 50-second cold-start penalty on the first upload.
- **Redis Broker** — mediates between the FastAPI orchestrator (which dispatches tasks) and the Celery worker (which executes them), decoupling request acceptance from processing completion.

The frontend observes extraction progress through a long-polling pattern: the backend returns a job identifier immediately upon upload, and the client polls a status endpoint every two seconds until the worker reports completion.

#### 3.1.2.3 Persistent Intelligence Domain

The persistence layer spans four specialized databases, each chosen for a distinct access pattern that no single database could serve optimally:

- **Redis** — in-memory cache for active session data (resume bindings, recent conversation turns) with 24-hour TTL-based eviction. Serves as the first-read tier in a three-level fallback chain.
- **MongoDB** — durable store for conversation history, session metadata, and raw uploaded files (via GridFS). Provides the source-of-truth for session restoration after Redis eviction.
- **Qdrant** — vector database storing 1024-dimensional BGE-M3 embeddings across four named vectors per resume (full_profile, skills, experience, education), enabling aspect-specific semantic search and skill-gap analysis.
- **Supabase (PostgreSQL)** — persistent, user-scoped resume storage that survives across chatbot sessions. A three-tier fallback chain (Redis → MongoDB → Supabase) ensures returning users can access their resume data without re-uploading.

This polyglot strategy reflects a deliberate architectural trade: operational complexity in managing four databases is accepted in exchange for each database serving its optimal access pattern — sub-millisecond reads from Redis, flexible document queries from MongoDB, high-dimensional similarity search from Qdrant, and relational integrity with Row Level Security from PostgreSQL.

```mermaid
flowchart TB
    subgraph "Synchronous Inference Domain"
        ORCH["FastAPI Orchestrator<br>(Intent Classification → Tool Dispatch → Response)"]
        OLLAMA["Ollama Inference Engine<br>(3 QLoRA Adapters on Qwen2.5:1.5B)"]
    end

    subgraph "Asynchronous Extraction Domain"
        BROKER["Redis Broker<br>(Task Queue)"]
        WORKER["Celery Worker<br>(PhoBERT NER + BGE-M3 Embeddings)"]
    end

    subgraph "Persistent Intelligence Domain"
        REDIS["Redis Cache<br>(Sessions, History)"]
        MONGO["MongoDB<br>(History, GridFS)"]
        QDRANT["Qdrant<br>(Resume Vectors)"]
        SUPA["Supabase/PostgreSQL<br>(User Profiles)"]
    end

    ORCH -->|"Adapter A/B/C inference"| OLLAMA
    ORCH -->|"Dispatch extraction task"| BROKER
    BROKER -->|"Consume task"| WORKER
    WORKER -->|"Store embeddings"| QDRANT
    WORKER -->|"Persist results"| MONGO
    WORKER -->|"Bind to session"| REDIS
    ORCH -->|"Session R/W"| REDIS
    ORCH -->|"History R/W"| MONGO
    ORCH -->|"Skill-gap search"| QDRANT
    ORCH -->|"User resume fallback"| SUPA
```

### 3.1.3 Container Topology

The system is deployed as a Docker Compose cluster comprising seven containers organized into three functional tiers, plus the Ollama inference engine running natively on the host. The containerization boundary is drawn precisely at the point where GPU access is required: all application logic, databases, and background workers run inside containers, while the inference engine that requires direct hardware access runs outside.

```mermaid
graph TB
    subgraph "Docker Compose Network"
        subgraph "Web Tier"
            NEXT["next-app<br>Next.js 16"]
        end

        subgraph "AI Tier"
            API["chatbot-api<br>FastAPI / Uvicorn"]
            CELERY["celery-worker<br>Celery (ml queue)"]
        end

        subgraph "Data Tier"
            REDIS["redis"]
            MONGO["mongodb"]
            ES["elasticsearch"]
            QDRANT["qdrant"]
        end
    end

    HOST["Ollama (Host)<br>GPU-accelerated"]

    NEXT -->|"BFF proxy"| API
    API -->|"Task dispatch"| REDIS
    CELERY -->|"Task consume"| REDIS
    API -->|"Session R/W"| REDIS
    API -->|"History R/W"| MONGO
    CELERY -->|"History R/W"| MONGO
    API -->|"Job search"| ES
    API -->|"Resume vectors"| QDRANT
    CELERY -->|"Embed + store"| QDRANT
    API -.->|"host-gateway bridge"| HOST
    CELERY -.->|"host-gateway bridge"| HOST
```

The Next.js frontend communicates with the FastAPI orchestrator exclusively through a Backend-For-Frontend (BFF) proxy layer, which normalizes upstream errors and ensures the backend is never directly exposed to the public network. The dashed lines to the Ollama node represent the host-gateway DNS bridge described in §3.1.4.1.

Docker Compose orchestrates the startup sequence through a health-gated dependency graph: data-tier services (Redis, MongoDB, Elasticsearch) must pass their health probes before AI-tier services are permitted to start, preventing connection failures during initialization. Qdrant uses a weaker `service_started` condition because the Celery worker lazily initializes its Qdrant client only upon the first CV upload, tolerating a brief startup window.

### 3.1.4 Design Tradeoffs

#### 3.1.4.1 CPU Containers with Host GPU Bridge

Running fine-tuned language models requires GPU hardware, yet configuring Docker GPU passthrough (via the Nvidia Container Toolkit) introduces significant operational complexity — driver version dependencies, runtime configuration, and potential conflicts with host processes. The architecture resolves this tension through a hybrid deployment: the Ollama inference engine runs natively on the host machine with direct GPU access, while the application logic remains fully containerized with CPU-only images.

Communication between containerized services and the host inference engine is established via Docker's DNS resolution mechanism (`host.docker.internal`), which resolves to the host machine's gateway address. This allows both the FastAPI orchestrator and the Celery worker to invoke Ollama's API without leaving the Docker network's logical boundary.

The container images are built from `python:3.11-slim` and explicitly target CPU-only PyTorch wheels, omitting the approximately 2 GB of CUDA runtime libraries that would otherwise bloat each image. System-level OCR dependencies (Tesseract with Vietnamese language support) are installed at build time, ensuring that scanned-document processing is available without additional host configuration.

This tradeoff yields a clean separation of concerns: containers encapsulate application dependencies and can be reproduced identically across development machines, while the host retains exclusive control over GPU resource allocation and model loading.

#### 3.1.4.2 Zero-Copy File Exchange

A fundamental bottleneck in distributed ML pipelines involving large file payloads is the serialization overhead of pushing binary data through a message broker. A 10 MB PDF encoded as Base64 expands to approximately 13.3 MB and must be serialized into a Redis message, transmitted, deserialized, and decoded — consuming broker memory and adding latency proportional to file size.

CareerIntel eliminates this overhead through a zero-copy exchange pattern using a shared Docker volume (`shared_tmp`):

```mermaid
sequenceDiagram
    participant API as FastAPI Orchestrator
    participant VOL as Shared Volume (/tmp)
    participant REDIS as Redis Broker
    participant WORKER as Celery Worker

    API->>VOL: 1. Write binary file to /tmp/{uuid}
    API->>REDIS: 2. Enqueue task with filepath string only
    REDIS->>WORKER: 3. Deliver lightweight task metadata
    WORKER->>VOL: 4. Read file directly from /tmp/{uuid}
    WORKER->>WORKER: 5. Begin extraction pipeline
```

The orchestrator writes the uploaded file to the shared volume and enqueues only the filepath string (tens of bytes) through Redis, rather than the file content (megabytes). The worker reads the file directly from the same volume mount, achieving zero serialization overhead regardless of file size. This pattern reduces broker memory pressure and eliminates the Base64 encoding/decoding latency entirely.

### 3.1.5 Request Lifecycle Flows

#### 3.1.5.1 Chat Request Pipeline

Every chat interaction traverses a nine-step pipeline that transforms a natural-language user message into an adapter-generated response. The pipeline demonstrates how the three computational domains collaborate at runtime:

```mermaid
flowchart LR
    subgraph "1. Session & Context"
        A["Resolve session<br>(Redis)"] --> B["Load resume<br>(Redis → Mongo<br>→ Supabase)"]
        B --> C["Build context window<br>(trim history<br>+ extractive summary)"]
    end

    subgraph "2. Intent Classification"
        D["Slash command<br>parser"] --> E{Match?}
        E -->|Yes| F["Direct ToolCall"]
        E -->|No| G["Adapter A<br>(JSON intent<br>classification)"]
        G --> H["Validate + retry<br>(temp 0.1 → 0.05<br>→ fallback)"]
    end

    subgraph "3. Tool Dispatch & Generation"
        I{Tool?}
        I -->|search_jobs| J["Elasticsearch<br>query"]
        I -->|assess_resume| K["Adapter B<br>+ CV JSON"]
        I -->|match_jobs| L["Qdrant skill-gap<br>→ Adapter B"]
        I -->|interview_prep| M["Adapter C<br>(tables/rubrics)"]
        I -->|general| N["Adapter B<br>(free-form)"]
    end

    C --> D
    F --> I
    H --> I
    J --> O["Response<br>envelope"]
    K --> O
    L --> O
    M --> O
    N --> O
```

The pipeline begins in the Persistent Intelligence Domain (session resolution, history retrieval, context window management), transitions through Adapter A's intent classification in the Synchronous Inference Domain, and branches into five execution paths — one of which (job search) queries Elasticsearch directly without invoking a language model, while the remaining four route through Adapters B or C for text generation.

A critical architectural feature is the **retry-with-temperature-drop strategy** for intent classification: if Adapter A's initial response fails JSON validation, the system retries at near-greedy temperature (0.05) before gracefully degrading to a general conversational response. This three-tier resilience ensures users always receive a meaningful reply, even when intent classification is uncertain.

#### 3.1.5.2 CV Upload Pipeline

The CV upload flow demonstrates the data transformation chain that converts an unstructured document into a structured, searchable, AI-ready representation:

```mermaid
flowchart LR
    subgraph "Stage 1: Ingestion"
        direction TB
        A["Binary file<br>(PDF / DOCX / Image)"] --> B["File validation<br>(type, size ≤ 20MB)"]
        B --> C["Write to shared volume<br>+ GridFS archival"]
    end

    subgraph "Stage 2: Text Extraction"
        direction TB
        D["PyMuPDF text layer"] --> E{Text empty?}
        E -->|Yes| F["OCR fallback<br>(Tesseract vie+eng<br>200 DPI rendering)"]
        E -->|No| G["Raw text"]
        F --> G
    end

    subgraph "Stage 4: Validation & Vectorization"
        direction TB
        M["CanonicalResume<br>(typed JSON schema)"] --> N["Quality scorer<br>(4 dimensions,<br>0–100 score)"]
        N --> O["BGE-M3 embedder<br>(4 × 1024-dim<br>named vectors)"]
        O --> P["Qdrant upsert<br>(vectors + payload)"]
    end

    subgraph "Stage 3: Semantic Structuring"
        direction TB
        H["Heuristic section<br>splitter<br>(11 regex patterns)"] --> I["Semantic chunker<br>(1 chunk per<br>logical unit)"]
        I --> J["Regex extractor<br>(email, phone, date,<br>GPA, URLs, skills)"]
        I --> K["PhoBERT NER<br>(PER, ORG, LOC)"]
        J --> L["Entity merge<br>(regex priority<br>for structured fields)"]
        K --> L
    end

    C -->|"Celery async"| D
    G --> H
    L --> M
    P --> Q["Session binding<br>(Redis + MongoDB<br>dual-write)"]
    
    C ~~~ M
    A ~~~ H
```

The pipeline transforms data through four increasingly structured representations:

| Stage | Input | Output | Transformation |
|-------|-------|--------|----------------|
| **Ingestion** | Binary file (PDF/DOCX/Image) | Raw bytes on shared volume | Format validation, zero-copy exchange |
| **Text Extraction** | Raw bytes | Unstructured text string | PyMuPDF parsing or Tesseract OCR fallback |
| **Semantic Structuring** | Flat text | `CanonicalResume` typed JSON | Section splitting → chunking → entity extraction → merge |
| **Validation & Vectorization** | Typed JSON | Quality-scored vectors in Qdrant | Multi-criteria scoring + BGE-M3 dense embeddings |

Each stage progressively adds structure and semantic meaning to the data. The unstructured binary input gains textual form through parsing, textual form gains semantic labels through entity extraction, and labeled entities gain mathematical representations through vectorization — culminating in a rich, searchable resume representation that downstream tools (CV assessment, job matching, interview preparation) can consume directly.

This same four-stage pipeline serves dual purposes: at training time (Chapter 8, Phases 2–3), it processes synthetic CVs to build the training dataset; at inference time (Chapter 7, §3.4.6), it processes real user uploads to populate the vector database. The architectural reuse ensures consistency between the data representations the model was trained on and those it encounters at runtime.


#### 3.2.2.2 Polyglot Persistence Architecture

#### 3.2.2.1 Overview

The AI chatbot operates across four distinct data access patterns that no single database can serve optimally: sub-millisecond reads of active session state, flexible document queries over unstructured conversation history, high-dimensional similarity search across vectorized resumes, and relational integrity for persistent user profiles with row-level tenant isolation. Rather than forcing these patterns into a single storage engine — accepting poor performance in at least three of the four — the system adopts a polyglot persistence strategy: each database is selected for the access pattern it was designed to optimize.

This chapter presents the architectural rationale behind the four-database topology, the data flows that connect them, and the design tradeoffs that govern their interaction. The focus is on three cross-cutting concerns: how session data moves through a lifecycle of creation, hydration, eviction, and restoration across database boundaries; how conversation state transforms from individual messages into a managed context window with extractive summarization; and how resume data flows from raw binary uploads through increasingly structured representations until it reaches a vector-searchable form. Chapter 1 introduced the Persistent Intelligence Domain as one of three computational domains; this chapter elaborates that domain's internal architecture in depth.

Redis provides the in-memory session cache — the first tier that every read request hits before falling through to slower, more durable stores. MongoDB serves as the durable document store for conversation history, session metadata, and raw binary files via GridFS, providing the source-of-truth that outlives Redis TTL eviction. Qdrant stores dense vector embeddings that enable semantic search and skill-gap analysis, capabilities that neither Redis nor MongoDB can provide. Supabase (PostgreSQL) provides the persistent, user-scoped storage layer with relational integrity and database-level access control, ensuring that resume data survives across chatbot sessions and that tenant isolation is enforced independently of application logic.

#### 3.2.2.2 Session Lifecycle Pipeline

A chatbot session passes through five distinct states as it moves across the persistence layer. Understanding this lifecycle is essential to understanding why the system writes the same data to two databases simultaneously and why it maintains a three-tier fallback chain for reads.

```mermaid
stateDiagram-v2
    [*] --> Created: User opens chat
    Created --> Active: Resume uploaded or first message
    Active --> Active: Subsequent messages (dual-write)
    Active --> Evicted: Redis TTL expires (24h)
    Evicted --> Restored: User returns (MongoDB fallback)
    Restored --> Active: Re-cached in Redis
    Active --> Persistent: User profile saved (Supabase)
    Persistent --> Active: New session + Supabase fallback
```

**Created → Active**: When a user initiates a conversation or uploads a resume, the system creates a session entry in Redis with a 24-hour time-to-live. If a resume is attached, the parsed JSON is bound to the session alongside the Qdrant vector identifier and the original filename. This initial write also propagates to MongoDB through an upsert operation, establishing the durable copy that will outlive the cache.

**Active → Active (Dual-Write)**: Every session update — new resume binding, conversation turn, context summary — writes to both Redis and MongoDB in sequence. Redis provides the sub-millisecond read latency required for real-time chat interactions; MongoDB provides the durability guarantee that survives cache eviction and service restarts. The system prioritizes write consistency over write performance: both writes must succeed before the operation returns, ensuring the durable store never lags behind the cache.

**Active → Evicted → Restored**: When a session's 24-hour TTL expires in Redis, the data is silently evicted. If the user returns, the system detects the cache miss and transparently falls through to MongoDB, retrieves the session data, re-caches it in Redis with a fresh TTL, and resumes the conversation as though no interruption occurred. This fallback is invisible to the user and to the upstream chat endpoint — the session store abstracts the recovery behind a single read interface.

**Active → Persistent**: For authenticated users, resume data is additionally persisted to Supabase (PostgreSQL), creating a user-scoped record that survives not just cache eviction but session expiration entirely. This enables the third fallback tier: when a returning user starts a new chatbot session, the system checks Supabase for previously analyzed resume data and injects it into the new session context, eliminating the need for re-upload.

The three-tier fallback chain — Redis → MongoDB → Supabase — reflects a deliberate architectural ordering from fastest-but-ephemeral to slowest-but-permanent. Each tier serves a different temporal scope: Redis holds active sessions (minutes to hours), MongoDB holds session history (days to weeks), and Supabase holds user profiles (indefinitely).

```mermaid
flowchart LR
    REQ["Session<br>read request"] --> R{Redis<br>cache hit?}
    R -->|Hit| RES["Return<br>session data"]
    R -->|Miss| M{MongoDB<br>session exists?}
    M -->|Found| RECACHE["Re-cache in Redis<br>+ return data"]
    M -->|Not found| S{Supabase<br>user profile?}
    S -->|Found| INJECT["Inject into<br>new session<br>+ return data"]
    S -->|Not found| EMPTY["No resume<br>context available"]
```

#### 3.2.2.3 Conversation State Machine

Conversation data undergoes a series of transformations as it moves through the persistence layer, progressing from individual user messages into a managed context window that fits within the small language model's token budget. This transformation pipeline is central to the system's ability to maintain coherent multi-turn conversations despite the base model's limited context capacity.

```mermaid
flowchart TD
    subgraph "Raw Input"
        A["User message<br>(natural language string)"]
    end

    subgraph "Persisted Turn"
        B["MongoDB document<br>(session_id, role,<br>content, timestamp)"]
        C["Redis list entry<br>(bounded to last<br>200 messages)"]
    end

    subgraph "Active Context Window"
        D["Trimmed history<br>(fits within 2,000-token<br>SLM budget)"]
    end

    subgraph "Compressed Memory"
        E["Extractive summary<br>(persisted to MongoDB,<br>injected into future prompts)"]
    end

    A -->|"Dual-write<br>(append)"| B
    A -->|"Dual-write<br>(append + trim)"| C
    B -->|"Full history<br>retrieval"| D
    D -->|"Older messages<br>trimmed"| E
    E -.->|"Prepended to<br>next context build"| D
```

**Raw Input → Persisted Turn**: Each user or assistant message is appended to both MongoDB (as an individual document with session linkage and chronological timestamp) and Redis (as a serialized entry in a bounded list). The MongoDB copy is the source-of-truth: it retains the complete conversation history without length constraints. The Redis copy is a performance optimization: it caches the most recent turns for fast retrieval during active conversations, automatically discarding older entries to prevent unbounded memory growth.

The MongoDB collection uses a compound index on session identifier and timestamp, enabling chronologically ordered retrieval of an entire conversation thread through a single index scan. This index design eliminates the need for a sort operation at query time — the storage layer returns messages in the order they were spoken.

**Persisted Turn → Active Context Window**: When the chat endpoint prepares a prompt for the language model, it retrieves the full conversation history from MongoDB and passes it through the Context Window Manager (detailed in Chapter 7). The manager evaluates the total token count against the model's 2,000-token budget and trims older messages from the beginning of the history until the remaining turns fit within the budget.

**Active Context Window → Compressed Memory**: When messages are trimmed, they are not simply discarded. The Context Window Manager generates an extractive summary of the dropped messages — a compressed representation that preserves the key topics, decisions, and user preferences from earlier in the conversation. This summary is persisted to MongoDB and prepended to the context window on subsequent requests, giving the model awareness of conversational history that has been evicted from the active window.

This summary-and-reinject pattern is the architectural answer to a fundamental constraint: the SLM's limited context window cannot hold long conversations, but users expect conversational continuity across dozens of turns. Rather than truncating silently (losing context) or paginating (adding complexity), the system compresses old context into a summary that occupies a fraction of the original token count while preserving the information most relevant to ongoing dialogue.

#### 3.2.2.4 Resume Data Pipeline

Resume data follows the most complex cross-database flow in the system, touching all four databases as it transforms from an unstructured binary file into a searchable, AI-ready vector representation. This pipeline is the persistence-layer counterpart to the four-stage CV Upload Pipeline described in Chapter 1 (§3.1.5.2) — where that section focused on the computational transformations (parsing, NER, embedding), this section traces the data's journey through the storage layer.

```mermaid
flowchart TD
    subgraph "Stage 1: Archival"
        A["Binary file<br>(PDF / DOCX / Image)"] --> B["GridFS<br>(MongoDB)<br>Raw binary archive"]
    end

    subgraph "Stage 2: Session Binding"
        C["Canonical Resume JSON<br>(from extraction pipeline)"] --> D["Redis session<br>(hot cache, 24h TTL)"]
        C --> E["MongoDB session<br>(durable copy)"]
    end

    subgraph "Stage 3: User Profile"
        F["Structured profile<br>(quality score,<br>skill counts)"] --> G["Supabase/PostgreSQL<br>(user-scoped,<br>persistent)"]
    end

    subgraph "Stage 4: Vectorization"
        H["4 text sections<br>(experience, skills,<br>education, full profile)"] --> I["BGE-M3 encoder<br>(1024-dim dense<br>embeddings)"]
        I --> J["Qdrant<br>(4 named vectors<br>+ metadata payload)"]
    end

    B -.->|"Extraction pipeline<br>(Celery worker)"| C
    D & E -.->|"If authenticated"| F
    C -.->|"Section text<br>extraction"| H
```

**Archival (MongoDB GridFS)**: The raw binary file is archived in MongoDB's GridFS immediately upon upload, before any processing begins. This archival serves two purposes: it provides an immutable record of the original document for audit and re-extraction, and it decouples the binary storage concern from the extraction pipeline — if extraction fails or needs to be re-run with improved algorithms, the original file is always available without requiring the user to upload again.

**Session Binding (Redis + MongoDB)**: Once the extraction pipeline produces a canonical resume JSON, the Celery worker binds it to the user's active session through the dual-write pattern described in §3.2.2. The resume JSON, the Qdrant vector identifier, and the original filename are written to both Redis and MongoDB, making the parsed resume immediately available to subsequent chat interactions. This binding is what enables the chatbot's resume-aware tools — CV assessment, job matching, interview preparation — to access the user's parsed profile without re-extraction.

**User Profile (Supabase)**: For authenticated users, the structured profile data — including the canonical resume JSON, quality score, and aggregate metrics (skill count, experience count) — is persisted to Supabase. This write is the bridge between session-scoped and user-scoped persistence: the session may expire, but the user profile endures. The data stored here is the same canonical JSON produced by the extraction pipeline, but associated with the user's identity rather than a transient session identifier.

**Vectorization (Qdrant)**: The extraction pipeline simultaneously generates four dense vector embeddings from different sections of the resume text, each encoding a different aspect of the candidate's profile. These vectors are stored as a single Qdrant point with four named vectors, enabling aspect-specific similarity search — a query against the skills vector returns resumes with similar skill profiles, while a query against the full profile vector returns holistically similar candidates.

The multi-vector architecture is a deliberate design choice that trades storage space (4× the vectors of a single-embedding approach) for retrieval precision. The chatbot's downstream tools exploit this granularity: job matching queries the skills vector for skill-gap analysis, while general resume search uses the full profile vector for holistic comparison. Each vector is accompanied by a metadata payload containing the candidate's structured attributes (seniority level, quality score, skill list), enabling filtered retrieval without secondary database lookups — the vector database serves as both the similarity engine and the metadata store for resume-aware operations.

#### 3.2.2.5 Tenant Isolation Architecture

The system enforces data isolation at two architectural levels: database-level policies that are evaluated on every query regardless of application logic, and application-level ownership filters that restrict operations to the requesting user's data.

**Database-Level Isolation (Supabase)**: The persistent user profile table enforces Row Level Security (RLS) policies directly in PostgreSQL, ensuring that every SELECT, INSERT, UPDATE, and DELETE operation is automatically filtered to the authenticated user's records. These policies are evaluated by the database engine itself — even a direct SQL query bypassing the application layer cannot access another user's data. The policies extract the authenticated user's identity from the JWT token and compare it against the ownership column on every row access.

The chatbot's backend service requires an exception to this isolation: the Celery worker performs server-side writes on behalf of users during asynchronous CV extraction, a context where no user JWT is available. This is resolved through a trust boundary decision — the worker connects with an elevated service-role key that bypasses RLS, while all user-facing endpoints connect with the user's scoped JWT. This bifurcation ensures that the least-privilege principle is maintained: user-facing code can never exceed the user's own data scope, while background workers operate under explicit, auditable elevated privileges.

**Application-Level Isolation (MongoDB)**: The conversation management layer enforces ownership isolation through query-level filtering — every read, update, and delete operation includes the user's identity as a mandatory filter predicate. This provides defense-in-depth: even if a user somehow obtains another user's conversation identifier, the query filter prevents cross-tenant access. MongoDB does not natively support row-level security policies comparable to PostgreSQL's, making this application-level enforcement the primary isolation mechanism for conversation data.

#### 3.2.2.6 Design Tradeoffs

#### 3.2.6.1 Four Databases vs. One

The polyglot persistence strategy introduces operational complexity: four databases to deploy, monitor, back up, and maintain, each with its own failure mode and scaling characteristics. The alternative — consolidating into PostgreSQL (which can serve as a cache via `UNLOGGED` tables, a document store via JSONB, and a vector store via pgvector) — would simplify operations at the cost of performance in at least two access patterns. Redis outperforms PostgreSQL for session reads by an order of magnitude, and Qdrant's HNSW index provides sub-100ms approximate nearest-neighbor search at a scale where pgvector's exact search degrades significantly. The system accepts the operational cost because the chatbot's real-time responsiveness depends on each database operating within its designed performance envelope.

#### 3.2.6.2 Dual-Write vs. Event Sourcing

The dual-write pattern (writing to both Redis and MongoDB in the same request path) introduces a consistency risk: if the MongoDB write fails after the Redis write succeeds, the cache contains data that the durable store does not. An event-sourcing architecture — where all state changes are appended to an immutable event log and materialized views are derived from replay — would eliminate this risk but add significant architectural complexity for a system where the failure mode is benign: a missed MongoDB write means the session cannot be restored after Redis eviction, but no data is corrupted. The system accepts this risk because session data is inherently ephemeral and can be regenerated by re-uploading a resume.

#### 3.2.6.3 Embedded Messages vs. Referenced Documents

Conversation messages in the sidebar's persistence layer are embedded as an array within the conversation document rather than stored as individual referenced documents. This trades write amplification (every new message rewrites the parent document's array) for read atomicity (loading a conversation retrieves the complete thread in a single query without joins). For a chatbot where conversations rarely exceed a few hundred messages, the document size remains well within MongoDB's 16 MB limit, and the read performance benefit — a single round-trip instead of a join across two collections — directly impacts the sidebar's perceived responsiveness when switching between conversations.


## 3.3 Frontend AI Presentation Layer (Next.js)

### 3.3.1 Overview

The frontend presentation layer serves as the user-facing coordination surface for the CareerIntel platform, bridging the interface with the synchronous inference and asynchronous processing domains (introduced in Chapter 1). Built on the Next.js App Router paradigm, the presentation layer translates user interactions into API orchestration calls while managing state reactivity, asynchronous machine learning tasks, and conversation history.

This chapter details the frontend orchestration architecture. It describes how the server-client rendering boundary isolates backend credentials while maintaining a responsive UI; how the asynchronous task pipeline handles file uploads, polling coordination, and backend failure mitigation; how conversation state integrates with the polyglot persistence layer; and how the presentation layer routes and renders responses based on upstream AI adapters. The chapter concludes with an analysis of the core architectural tradeoffs governing the presentation layer's design.

### 3.3.2 Server-Client Rendering Boundary

The presentation layer utilizes the Next.js App Router to separate server-side data fetching and authentication from client-side UI reactivity. Rather than mixing credential management with UI execution, the architecture enforces a strict **Trust Boundary Pattern** that dictates where application logic is executed.

```mermaid
flowchart TD
    subgraph Browser ["Client-Side Browser Runtime (Reactivity Layer)"]
        UI["Interactive UI Components<br>(State, Events, CV Upload)"]
    end
    subgraph Boundary ["Trust Boundary"]
        BFF["Next.js BFF API Routes<br>(Auth & Session Validation)"]
    end
    subgraph Server ["Secure Server-Side Runtime (Access Layer)"]
        SC["Next.js Server Components<br>(Initial Page Hydration)"]
        BE["FastAPI Orchestrator<br>(Synchronous Inference Domain)"]
    end

    UI -->|"Interactive actions"| BFF
    BFF -->|"Credentialed calls"| BE
    SC -->|"Direct reads"| BE
```

#### 3.3.2.1 Secure Server Components
The entry point for the conversational interface (`/ai`) runs exclusively within the secure server runtime. Server Components manage:
- **Credential Isolation**: Performing tenant authentication and session verification without exposing database connection strings, security tokens, or environment keys to the browser.
- **Initial Hydration**: Querying the FastAPI orchestrator directly during page generation to retrieve the user's active session metadata and recent conversation list. This eliminates the latency of a secondary client-side API round-trip during the initial load.

#### 3.3.2.2 Reactive Client Components
The interactive chat elements operate inside the client-side browser runtime, separated by the `"use client"` declaration boundary. Client Components handle:
- **Interactive State**: Maintaining the local message feed, capture of file-upload payloads, and dynamic sidebar updates in response to user inputs.
- **Micro-interactions**: Orchestrating local layout adjustments, typing indicators, and user-initiated actions that require immediate response without server latency.

---

### 3.3.3 Asynchronous Task Coordination Pipeline

Processing unstructured resumes involves computationally heavy tasks (such as parsing, Named Entity Recognition, and embedding generation) that exceed standard HTTP timeout limits. To keep the UI responsive, the presentation layer orchestrates uploads and status checks through a decoupled, asynchronous pipeline mediated by a Backend-For-Frontend (BFF) proxy.

```mermaid
sequenceDiagram
    participant Client as Client Component (Browser)
    participant BFF as Next.js BFF Proxy
    participant Backend as FastAPI Orchestrator
    participant Queue as Redis Broker / Celery Worker
    
    Client->>BFF: 1. Ingest document (FormData)
    BFF->>Backend: 2. Forward payload with user context
    Backend->>Queue: 3. Dispatch Celery task & write file reference
    Backend-->>BFF: 4. Return Job ID (PENDING)
    BFF-->>Client: 5. Return normalized Job ID
    
    loop Status Polling
        Client->>BFF: 6. Request job status (Job ID)
        BFF->>Backend: 7. Check task execution state
        Backend-->>BFF: 8. Return task status (PENDING/RUNNING)
        BFF-->>Client: 9. Return normalized state
    end
    
    Note over Backend, Queue: Celery worker completes PhoBERT NER & Qdrant embedding
    
    Client->>BFF: 10. Request job status (Job ID)
    BFF->>Backend: 11. Check task execution state
    Backend-->>BFF: 12. Return COMPLETED (Session ID)
    BFF-->>Client: 13. Return normalized state with context bindings
    Client->>Client: 14. Bind session context & transition view
```

#### 3.3.3.1 Ingestion and Task Dispatch
When a user attaches a CV, the presentation layer captures the file, runs initial type checks, and transmits the payload to the BFF upload proxy. The BFF forwards the request to the FastAPI orchestrator, which archives the raw document in MongoDB GridFS, writes the file to the shared volume, and dispatches a background processing task to the Redis-backed Celery worker (as described in §3.1.4.2). The API immediately returns a unique job identifier, freeing the client from waiting for the extraction process to complete.

#### 3.3.3.2 Status Polling and Progress Tracking
Upon receiving the job identifier, the client UI transitions to a processing state and enters a polling loop. The client queries the BFF status endpoint at regular intervals to trace task execution. If the task remains active, the UI displays dynamic progress updates to manage user expectations. If the task fails or times out, the client handles the transition gracefully, allowing the user to retry without losing conversation state.

#### 3.3.3.3 BFF Error Normalization Boundary
The Next.js API routes act as an **Error Normalization Boundary** between the frontend and the upstream AI services. If the FastAPI backend encounters a database timeout, an out-of-memory error during inference, or is temporarily unreachable, the BFF intercepts these raw failures. Instead of exposing raw stack traces or throwing unhandled exceptions that could crash the React UI, the BFF normalizes these responses into a standard JSON error payload. This structure allows the client component to transition to a controlled error state and offer context-specific recovery paths.

---

### 3.3.4 Conversation State Architecture

The conversational sidebar manages active session states, historical list retrieval, and session renaming or archiving. This layer interacts directly with Chapter 3's polyglot persistence architecture.

#### 3.3.4.1 Conversation Lifecycles
Conversation documents are persisted in MongoDB (as described in §3.2.5). The presentation layer manages these states through server-side CRUD endpoints:
- **Title Generation**: To eliminate manual title entry, the system automatically derives a thread title from the initial user turn, trimming it to fit the sidebar constraints.
- **Soft Deletion**: Archiving operations mark records as soft-deleted to keep the sidebar list clean while preserving historical records for potential restoration.
- **Tenant Isolation**: Every CRUD operation is verified at the BFF layer by cross-checking the requester's authenticated identifier against the record owner, preventing cross-tenant access.

#### 3.3.4.2 Session Identity Linkage
When a conversation starts, it receives a client-side identity. If the user subsequently uploads a resume, the extraction pipeline binds the generated parsed context to a backend session ID (see §3.2.4). The presentation layer links these identifiers together. When a user switches between sidebar conversations, the client passes the linked backend session ID to the FastAPI orchestrator, allowing the backend to restore vector search parameters and retrieve CV embeddings from Qdrant without reprocessing the original document.

---

### 3.3.5 Response Rendering Pipeline

The presentation layer uses a **Presentation Router Pattern** to handle structured outputs from the different backend AI adapters. The frontend acts as a template compiler, routing responses based on their declared type to ensure specialized data formats are rendered correctly.

```mermaid
flowchart TD
    Env["JSON Response Envelope<br>(Markdown, Metadata, Task Type)"] --> Router{"Presentation Router"}
    
    Router -->|search_jobs| JobCards["Structured Job Cards<br>(Salary, Location, Direct Link)"]
    Router -->|assess_resume / general_response| MD["Markdown Coach Prose<br>(Paragraphs, Lists, Inline Code)"]
    Router -->|match_jobs| Gap["Skill-Gap Analysis<br>(Matched vs. Missing Lists)"]
    Router -->|interview_prep| Tables["Markdown Tables<br>(Question-Rubric Matrices)"]
    Router -->|needs_resume| Widget["Contextual Actions<br>(CV Upload Prompt)"]
```

#### 3.3.5.1 Task-Type Presentation Routing
The backend returns a unified JSON response envelope containing the text payload, execution metadata, and a classification label (`task_type`). The presentation layer parses this label and routes the payload to the appropriate UI layout:
- **Coaching and Conversations** (`assess_resume`, `general_response`): Routed to the standard Markdown renderer, displaying paragraphs, bold highlights, lists, and inline code generated by Adapter B.
- **Structured Preparation Matrices** (`interview_prep`): Formatted as multi-column Markdown tables that align interview questions, candidate evaluation rubrics, and recommended study paths generated by Adapter C.
- **Job Search Listings** (`search_jobs`): Bypasses standard Markdown rendering. The UI compiles the raw search results from Elasticsearch into structured, interactive job cards containing salary badges, locations, and direct application links.
- **Skill Gap Assessments** (`match_jobs`): Renders visual lists that compare candidate skills against job requirements, grouping them into matched and missing lists for easy scanning.
- **Contextual Actions** (`needs_resume`): Renders helper prompts and action buttons (such as triggering the file attachment workflow) when a resume is required but has not yet been bound to the session.

---

### 3.3.6 Design Tradeoffs

#### 3.3.6.1 Asynchronous Long-Polling vs. WebSockets vs. SSE
The choice of client-polling over persistent connection protocols (such as WebSockets or Server-Sent Events) represents a trade of connection overhead for system simplicity:
- **WebSockets and SSE**: Offer lower latency and real-time push capability, but they require persistent server connections. This complicates load balancing, increases memory consumption at the BFF layer under high concurrent loads, and requires complex client-side reconnection logic.
- **Long-Polling**: Operates over standard, stateless HTTP requests. It works out-of-the-box with serverless and edge infrastructure, integrates with standard authentication models, and avoids holding open long-lived sockets. Polling every two seconds introduces negligible network overhead for the relatively low frequency of CV uploads, while drastically simplifying the BFF deployment.

#### 3.3.6.2 BFF Error Normalization vs. Upstream Proxying
The error normalization boundary adds development complexity but significantly increases frontend resilience:
- **Upstream Proxying**: Directly forwarding raw backend responses reduces BFF code and simplifies debugging during development, but it exposes the client to raw framework errors, database tracebacks, or system timeouts.
- **BFF Error Normalization**: Intercepting and wrapping all upstream exceptions into standardized frontend states ensures the client UI never crashes due to unexpected backend failures. This trade prioritizes user-facing durability and graceful degradation over raw error visibility.

#### 3.3.6.3 Embedded Messages vs. Client-Side State Management
Managing conversation state directly through server-side MongoDB reads (leveraging the embedded messages structure in §3.2.6.3) trades client-side flexibility for structural simplicity:
- **Client-Side State Management**: Using complex global state containers allows for advanced offline editing and client-side filtering, but it increases code bundle sizes and introduces consistency issues when sync operations fail.
- **Embedded Messages**: Keeps the client state stateless. Clicking a conversation fetches the entire thread in a single, fast document query. The UI remains simple, reactivity is handled by React's local state, and the server retains the authoritative conversation history, ensuring a consistent user experience across multiple devices.


## 3.4 AI Chatbot Orchestrator — SLM Multi-Adapter Architecture

### 3.4.1 Overview

The AI chatbot orchestrator serves as the central coordination surface of the CareerIntel platform. It organizes real-time user interactions through a **Multi-Adapter Small Language Model (SLM) architecture**, in which three specialized adapters—fine-tuned via QLoRA—are mounted on a single shared Qwen2.5:1.5B base weights model. Rather than relying on a monolithic model configured with varying system prompts, this architecture decomposes the user experience into task-specific sub-problems. This approach minimizes latency, ensures predictable output formatting, and fits within the memory constraints of consumer-grade hardware.

The orchestrator is structured around a FastAPI server that acts as a traffic router. It resolves session state, determines intent using **Adapter A** (intent classifier), and delegates execution to the **Tool Dispatcher**. The dispatcher routes requests to specialized search indices or downstream generation adapters: **Adapter B** (HR career coach) for natural Vietnamese prose, or **Adapter C** (structured content generator) for interview preparation matrices and roadmap tables.

```mermaid
flowchart TB
    USER["User Message"] --> SERVER["FastAPI Orchestrator"]
    SERVER --> SLASH["Slash Command Parser"]
    SERVER --> ADAPTER_A["Adapter A: Classifier"]
    ADAPTER_A -->|"Structured JSON"| DISPATCH["Tool Dispatcher"]
    SLASH -->|"Direct ToolCall"| DISPATCH
    
    DISPATCH -->|"search_jobs"| ES["Elasticsearch Search Engine"]
    DISPATCH -->|"assess_resume"| ADAPTER_B["Adapter B: HR Coach"]
    DISPATCH -->|"match_jobs"| QDRANT["Qdrant + Adapter B"]
    DISPATCH -->|"interview_prep"| ADAPTER_C["Adapter C: Structured Gen"]
    DISPATCH -->|"general_response"| ADAPTER_B
```

---

### 3.4.2 Multi-Adapter Design

#### 3.4.2.1 Design Rationale

Partitioning the platform's features across three specialized adapters rather than a single general-purpose model addresses a fundamental constraint: small language models (under 3 billion parameters) suffer a severe performance drop when forced to generalize across structured and unstructured domains simultaneously. A model fine-tuned for empathetic Vietnamese conversation struggle to consistently generate valid, un-nested JSON or rigid markdown tables. 

Decomposing these tasks yields three core benefits:
- **Inference Latency Optimization**: Each adapter's generation parameters are tuned to its task length and complexity. The classification adapter executes with tight token bounds in under a second, while the prose generation adapter is permitted a larger token budget.
- **Syntactic Reliability**: The classification adapter is bound to structured JSON syntax through inference-level constraints, avoiding the need for complex regular expression repair functions on the application side.
- **Resource Footprint Conservation**: By sharing the base weights of the 1.5B model in GPU memory and hot-swapping the lightweight adapter matrices (QLoRA weights), the orchestrator runs efficiently on a single consumer GPU or CPU instance without reloading the core base weights.

#### 3.4.2.2 Parameter Tuning and Generation Strategy

The generation parameters for each adapter are mapped dynamically at the orchestrator level, tailoring model behavior to the safety and creativity requirements of each task:

- **Intent Classifier (Adapter A)**: Configured with a near-greedy temperature ($0.1$) and a low max-token boundary ($256$). This ensures high predictability and deterministic routing.
- **Career Coach (Adapter B)**: Configured with a moderate temperature ($0.5$) and a mid-range token limit ($1024$) to allow fluent, natural-sounding Vietnamese prose while maintaining strict factual grounding in the candidate's CV data.
- **Structured Generator (Adapter C)**: Configured with a low-to-moderate temperature ($0.3$) and a high token limit ($2048$) to generate comprehensive, properly formatted multi-column markdown tables without truncation.

During developmental phases where specialized weights are not initialized, the orchestrator routes calls to the vanilla base model. This fallback enables complete pipeline testing and verification before fine-tuning is completed.

---

### 3.4.3 Intent Classification Pipeline

#### 3.4.3.1 Constrained Generation and Intent Routing

The intent router is the gateway of the chat execution pipeline, translating unstructured user queries into machine-readable tool execution schemas. The classification adapter (Adapter A) is trained to parse the user message and emit a JSON object containing the target tool name and normalized parameters.

A key design choice is that the classification step is **stateless and single-turn**. The orchestrator does not feed historical message threads to Adapter A. This design decision directly reflects the dataset synthesis process (detailed in Chapter 8), which trains the classifier exclusively on single-turn user utterances. By stripping conversational history from the classification prompt, the system prevents context drift from biasing intent routing.

#### 3.4.3.2 Resilience and Override Logic

To safeguard the orchestrator against malformed JSON outputs or parameter parsing errors, the intent router implements a multi-tier **Resilience Cascade**:

```mermaid
flowchart TD
    MSG["User Message"] --> TRY1["Attempt 1: Adapter A<br>(temp = 0.1)"]
    TRY1 --> PARSE1{"JSON & Schema Valid?"}
    PARSE1 -->|"Yes"| RETURN["Return Tool Call"]
    PARSE1 -->|"No"| TRY2["Attempt 2: Adapter A<br>(temp = 0.05)"]
    TRY2 --> PARSE2{"JSON & Schema Valid?"}
    PARSE2 -->|"Yes"| RETURN
    PARSE2 -->|"No"| FALLBACK["Fallback: general_response"]
    FALLBACK --> RETURN
```

1. **Attempt 1 (Standard Sampling)**: Adapter A is run at temperature $0.1$. The output is validated against structured schema definitions, normalizing user inputs (such as matching Vietnamese location synonyms to indexed cities).
2. **Attempt 2 (Near-Greedy Decoding)**: If validation fails, the orchestrator retries the inference at a reduced temperature of $0.05$. Lowering the sampling variance resolves boundary cases where the model oscillates between two competing tools.
3. **Conversational Fallback**: If the retry fails to generate valid structured data, the router falls back to a conversational response task type (`general_response`), routing the message to the prose coach (Adapter B) to maintain interaction continuity.

Downstream of the router, the orchestrator applies a **Context-Aware Override** for conversational edge cases. Small language models struggle to map short, context-dependent affirmative phrases (such as "ok" or "có") to complex tools without historical context. If the classifier yields a `general_response` but the session has an active resume and the preceding assistant turn prompted the user for CV evaluation, the orchestrator overrides the intent classification to `assess_resume`. This hybrid pattern combines the high speed of stateless classification with the accuracy of stateful, heuristic state corrections.

---

### 3.4.4 Tool Dispatch Architecture

#### 3.4.4.1 Dispatch as a Strategy Pattern

The Tool Dispatcher acts as a Strategy Pattern coordinator, translating the structured tool calls into concrete backend operations. Based on the selected tool, the dispatcher gathers required inputs, queries data indices or vector stores, constructs prompt contexts, and selects the target generation adapter.

The dispatcher coordinates five execution strategies:

| Tool Intent | Data Source | Primary Adapter | Core Output Modality |
| :--- | :--- | :--- | :--- |
| `search_jobs` | Elasticsearch | None (Direct Query) | Structured Job Listing Cards |
| `assess_resume` | MongoDB (Resume JSON) | Adapter B (HR Coach) | Formatted Performance Prose |
| `match_jobs` | Qdrant (Vectors) | Adapter B (HR Coach) | Skill-Gap Analysis Narrative |
| `interview_prep` | MongoDB (Resume JSON) | Adapter C (Structured Gen) | Question-Rubric Tables / Roadmaps |
| `general_response` | MongoDB (Session History) | Adapter B (HR Coach) | Conversational Vietnamese Dialogue |

```mermaid
flowchart TD
    TC["Tool Call"] --> SW{"Tool Type?"}
    SW -->|"search_jobs"| ES["Elasticsearch Faceted Query"]
    SW -->|"assess_resume"| B1["Adapter B + CV Context"]
    SW -->|"match_jobs"| QD["Qdrant Skill Gap Analysis + Adapter B"]
    SW -->|"interview_prep"| C1["Adapter C (Roadmap or Rubric Table)"]
    SW -->|"general_response"| B2["Adapter B Free-form Prose"]
    
    ES --> OUT["Response Envelope"]
    B1 --> OUT
    QD --> OUT
    C1 --> OUT
    B2 --> OUT
```

#### 3.4.4.2 Slash Commands as Deterministic Bypass

For power users and predictable workflows, the orchestrator supports deterministic slash commands (such as `/coach`, `/match`, and `/interview`). The parser intercepts these commands at the entry point of the chat pipeline, bypassing Adapter A's inference step entirely. This design optimization reduces server latency to zero for structured requests while ensuring absolute classification accuracy.

---

### 3.4.5 Context Window Management

#### 3.4.5.1 The Token Budget Constraint

Although modern SLM architectures support long context limits in theory, quantized 1.5B parameter models experience severe semantic degradation when inputs exceed a few thousand tokens. In long conversations containing parsed CV structures and multiple turn histories, attention heads lose coherence, leading to repetitive or irrelevant generation. To maintain coherence, the orchestrator enforces a strict token budget.

#### 3.4.5.2 Sliding Window with Extractive Summarization

The orchestrator manages context using a two-tier budget: a **history budget** ($2,000$ tokens) for verbatim message tracking and a **summary budget** ($500$ tokens) for historical memory. When history exceeds this limit, the oldest turns are evicted from the active window and routed to a zero-latency **Extractive Summarizer**.

The summarizer extracts key information using lightweight heuristics rather than costly LLM compression passes:
1. **Initial Intent**: Captures and retains the first user message of the thread.
2. **Boundary Continuity**: Preserves the final message of the evicted block to maintain structural transition.
3. **Keyword Filtering**: Scans evicted messages for high-signal career-related keywords (e.g., CV, skills, salary, interviews) and retains matches.

The resulting summary is prepended to subsequent generations as a specialized system message. This ensures the model retains historical context without blowing through its token budget.

---

### 3.4.6 Asynchronous Task Tracking

Because parsing unstructured CV documents, performing named entity extraction, and generating multi-vector embeddings are computationally intensive tasks ($30$ to $180$ seconds), the orchestrator offloads this work to background Celery workers via a Redis broker.

This asynchronous pipeline uses two primary optimizations:
- **Model Warmup**: To eliminate the $50$-second cold-start latency associated with initial PyTorch model loading, the background workers execute dummy inference passes for the NER and embedding models during process startup. This pre-warms the attention weights and CUDA compilation kernels.
- **Transient State Tracking**: The orchestrator registers and updates job states (`PENDING` $\rightarrow$ `PROCESSING` $\rightarrow$ `COMPLETED` or `FAILED`) in Redis with a one-hour time-to-live. Once complete, the worker triggers a dual-write binding to both Redis and MongoDB (as detailed in §3.2.2) to make the structured resume context immediately available to the chat loop.

---

### 3.4.7 Design Tradeoffs

#### 3.4.7.1 Stateless vs. Stateful Intent Classification

Using a stateless classifier (Adapter A) ensures rapid, predictable intent routing, but prevents the model from resolving conversational dependencies (such as short affirmative answers to previous questions). Rather than resolving this by passing the full history to the classifier—which would increase latency and introduce intent drift—the system combines a stateless classifier with a stateful server-side heuristic override. This hybrid model keeps inference fast and predictable while resolving conversational dependencies at the application layer.

#### 3.4.7.2 Multi-Adapter Decomposition vs. Monolithic LLM

Decomposing the application into three task-specific QLoRA adapters trades single-model simplicity for inference-time flexibility and resource efficiency. A single monolithic LLM would simplify application-level routing but requires significantly higher hardware specifications (VRAM and compute) and yields lower accuracy on structured generation tasks. The multi-adapter pattern allows a tiny 1.5B model to achieve task-specific alignment at a fraction of the hardware cost.

#### 3.4.7.3 Extractive vs. Abstractive Summarization

To manage context limits, the system utilizes a rule-based extractive summarizer rather than a generative LLM-based summarization task. Generative summarization produces smoother narrative summaries but adds secondary inference latency to the chat pipeline and risks introducing model hallucinations. The extractive approach uses zero-latency keyword indexing to extract raw, factual segments, preserving context integrity at zero runtime cost.


## 3.5 ML Training Pipeline — Data-to-Adapter Architecture

### 3.5.1 Overview

While Chapter 7 documents the multi-adapter runtime orchestrator, this chapter details the offline training pipeline designed to produce and align the specialized adapter models. The pipeline operates as a sequential data transformation pipeline, shifting unstructured data configurations through specialized learning representations to produce three task-specific QLoRA adapters. The training process runs end-to-end on a single NVIDIA RTX A5000 GPU ($24$ GB VRAM) within approximately $13$ hours.

```mermaid
flowchart TD
    P1["Phase 1: Synthetic CV Generation"] -->|"500 Resumes (JSON/PDF)"| P2["Phase 2: Extraction Cascade"]
    P2 -->|"Canonical Schema"| P3["Phase 3: Validation & Vector Storage"]
    P3 -->|"Validated Resumes"| P4["Phase 4: Task-Specific RAG Seeds"]
    P4 -->|"SFT/DPO Inputs"| P5["Phase 5: Dataset Synthesis"]
    P5 -->|"ChatML Datasets"| P6["Phase 6: QLoRA & DPO Training"]
    P6 -->|"Task Adapters"| P7["Phase 7: LLM-as-Judge Benchmark"]
```

The pipeline progresses from raw domain specifications to validated adapter models through a continuous flow of data representations:
$$\text{Role Configurations} \rightarrow \text{Structured CV Content} \rightarrow \text{Canonical Schema} \rightarrow \text{Quality-Scored Vector Embeddings} \rightarrow \text{Task Seed Outputs} \rightarrow \text{ChatML Datasets} \rightarrow \text{QLoRA Adapters}$$

---

### 3.5.2 Synthetic Data Foundation

#### 3.5.2.1 Rationale for Synthetic Resumes
Fine-tuning the specialized adapters requires a dense training dataset containing diverse professional profiles with predetermined quality characteristics. Relying on real-world resumes presents two major challenges: privacy regulations (PII) restrict the storage and processing of candidate profiles, and real-world resumes lack structured quality controls. To train the HR coaching adapter to distinguish strengths from weaknesses, the training pipeline must control the presence of vague accomplishments, missing metrics, and formatting anomalies.

Synthetic generation resolves these issues by deterministically configuring candidate demographics, experience timelines, and professional details. This strategy allows the pipeline to assign ground-truth metadata tags—such as seniority levels, target domains, and overall quality flags—which serve as training labels and evaluation benchmarks.

#### 3.5.2.2 Generation and Rendering Transformation
The synthetic generation process functions as a three-stage pipeline:
1. **Configuration Mapping**: The generator loads YAML definitions for $36$ distinct roles across seven industry domains. These configurations define skill taxonomies, educational standards, and role-specific performance metrics.
2. **LLM Content Generation**: A local $14$B parameter base model generates structured Vietnamese CV content. Crucially, the generator triggers a degraded mode for $10\%$ of the generated batch, forcing the model to omit performance metrics, write generic descriptions, and leave sections incomplete. This creates the ground-truth contrast required for the evaluation suite.
3. **Format Rendering**: The generated JSON structures are rendered into PDF and HTML documents using LaTeX templates, ensuring that the visual formatting matches standard professional layouts.

---

### 3.5.3 Data Structuring Pipeline

```mermaid
flowchart LR
    RAW["Raw CV Text"] --> SEG["Semantic Segmentation"]
    SEG --> EXT["Extraction Cascade (Regex + NER)"]
    EXT --> NORM["Canonical Normalization"]
    NORM --> VAL["Quality Scorer & Validator"]
    VAL --> STOR["Vector & Document Storage"]
```

#### 3.5.3.1 Semantic Extraction Cascade
The raw text parsed from generated resumes is mapped to a structured, typed `CanonicalResume` data contract through a multi-stage cascade:
- **Semantic Segmentation**: The document is partitioned into logical blocks (personal info, experience, education, skills, projects) using regex-based heading heuristics rather than arbitrary token boundaries.
- **Extraction Cascade**: A parallel regex and Transformer-based Named Entity Recognition (NER) pipeline processes each segment. Regex rules extract deterministic formats (emails, phone numbers, GPA, URLs, date ranges), while a pre-trained PhoBERT model extracts contextual entities such as organization names, locations, and candidate names.
- **Canonical Normalization**: Extracted entities are merged, prioritizing deterministic regex outputs for structured fields, and compiled into the canonical schema.

#### 3.5.3.2 Quality Scoring and Vector Indexing
Once normalized, the candidate profiles undergo validation and indexing:
- **Logical Validation**: The validator identifies temporal overlaps in employment history, reversed date ranges, and out-of-scale GPAs, recording anomalies as validation alerts.
- **Quality Scorer**: A heuristic scorer evaluates the resume across four dimensions: completeness ($30\%$), specificity ($40\%$, checking for quantified metrics versus vague verbs), consistency ($20\%$, penalizing validation errors), and presentation ($10\%$, checking document length and link presence). Profiles scoring below $45$ are flagged as low-quality.
- **Multi-Vector Storage**: High-dimensional embeddings are generated across four independent representations (full profile, skills, experience, education) using a multi-lingual embedding model. The vectors are indexed in Qdrant to support task-specific semantic retrieval, while the structured profiles are persisted in MongoDB.

---

### 3.5.4 Task Seed Generation

Using the multi-vector indices, the pipeline runs RAG execution passes to produce task-specific seed data for training. The orchestrator injects candidate-specific profile contexts into specialized target prompts to generate three output modalities:
1. **CV Assessment**: Generates structured, constructive Vietnamese coaching feedback using a senior HR consultant persona. High-quality resumes receive reinforcement and polish suggestions; low-quality resumes receive detailed analysis of omissions and action-oriented rewrites of vague achievements.
2. **Job Matching**: Performs vector-based similarity matching against a database of active job descriptions, identifying key skill gaps, missing qualifications, and candidate-to-role suitability scores.
3. **Interview Preparation**: Generates tailored technical questions based on the candidate's documented projects, accompanied by multi-tiered scoring rubrics ($0$ to $4$ points) for hiring managers.

---

### 3.5.5 Dataset Architecture

To ensure the adapters adapt to the runtime orchestration environment, all training inputs are formatted as three-turn ChatML messages, matching the system prompts and boundaries they will receive at inference time.

The training pipeline compiles four distinct datasets:
- **Adapter A (Classifier)**: Built from intent classification queries, using data expansion and paraphrasing to cover linguistic variations of tool execution commands.
- **Adapter B (HR Coach)**: Formed by combining positive feedback seeds and critical assessment outputs, training the model to calibrate its feedback tone based on resume quality.
- **Adapter C (Structured Gen)**: Composed of structured markdown templates, interview question lists, and tabular learning roadmaps.
- **Adapter B (DPO)**: Created by pairing positive target outputs (Gemini teacher feedback) with rejected target outputs (untuned base model outputs) to optimize preference alignment.

| Dataset Target | Primary Purpose | SFT Train | SFT Val | DPO Pairs | Avg Token Length |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Adapter A** | Intent Classification | $4,869$ | $542$ | — | $355$ |
| **Adapter B** | Empathy & Metric Coaching | $1,656$ | $185$ | $1,841$ | $1,490$ |
| **Adapter C** | Markdown Tables & Rubrics | $820$ | $92$ | — | $1,024$ |

---

### 3.5.6 Training Architecture

#### 3.5.6.1 QLoRA Parameter Efficiency
The core training architecture relies on QLoRA to fine-tune the $1.5$B base weights model within consumer-grade hardware limits ($2$ GB VRAM footprint for base weights). The base model parameters are frozen and quantized into $4$-bit NormalFloat (NF4) with double quantization enabled. Trainable low-rank parameter matrices (rank $r=16$, scaling $\alpha=32$) are injected across all seven attention and MLP linear projections, representing approximately $0.5\%$ ($7.5$ million parameters) of the total network footprint.

#### 3.5.6.2 Three-Layer Stacked DPO Alignment
To align the coaching adapter (Adapter B) with human feedback preferences, the pipeline applies Direct Preference Optimization (DPO) using the Bradley-Terry preference model:
$$\mathcal{L}_{\text{DPO}} = -\mathbb{E}_{(x, y_w, y_l) \sim D} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} \right) \right]$$
where $y_w$ represents the chosen Gemini feedback, $y_l$ represents the rejected base model output, and $\beta=0.1$ controls the strength of the KL-divergence constraint relative to the reference model.

```mermaid
flowchart TD
    BASE["Layer 1: Base Qwen2.5-1.5B (4-bit NF4)<br>Frozen"]
    SFT["Layer 2: SFT Adapter (cv-coaching)<br>Frozen"]
    DPO["Layer 3: DPO Adapter (preference alignment)<br>Trainable"]
    
    BASE --> SFT
    SFT --> DPO
```

Rather than fine-tuning the SFT weights directly—which leads to performance degradation and formatting drift in small models—the pipeline stacks a new trainable DPO adapter layer on top of the frozen SFT adapter weights, maintaining a clear separation between domain formatting knowledge and style preference alignment.

#### 3.5.6.3 Fine-Tuning Performance Summary
All three adapters were trained sequentially, using a paged 8-bit AdamW optimizer and cosine learning rate schedules:

| Adapter | Phase | Train Loss | Eval Loss | Compute Time | Saved Size |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Adapter A: Classifier** | SFT | $0.1537$ | $0.0918$ | $5.6$ hours | $81.4$ MB |
| **Adapter B: HR Coach** | SFT | $0.2837$ | $0.4901$ | $1.8$ hours | $81.4$ MB |
| **Adapter B: HR Coach** | DPO | $0.0345$ | $< 0.001$ | $4.3$ hours | $81.4$ MB |
| **Adapter C: Structured Gen** | SFT | $0.9651$ | $0.8684$ | $1.6$ hours | $81.4$ MB |

---

### 3.5.7 Evaluation Results

An automated evaluation framework running Gemini 3.1 Pro as an external judge benchmarks the pipeline and fine-tuned adapters against the unaligned base models across four evaluation tracks:

| Track | Target Component | Base Model Score | Fine-Tuned Adapter | Pass Threshold | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **1. Extraction** | Parsing Cascade | — | $97.3\%$ Schema Accuracy | $\ge 80.0\%$ Accuracy | ✅ PASS |
| **2. HR Feedback** | Adapter B (DPO) | $1.2 / 10$ | $7.8 / 10$ | $\ge 7.0 / 10$ | ✅ PASS |
| **3. Tool Calling** | Adapter A (Classifier) | $50.0\%$ | $98.0\%$ Accuracy | $\ge 90.0\%$ Accuracy | ✅ PASS |
| **4. Structured Gen** | Adapter C (Structured) | $3.6 / 10$ | $8.1 / 10$ | $\ge 7.0 / 10$ | ✅ PASS |

The benchmark results demonstrate three major architectural findings:
1. **Necessity of Adapter Tuning**: Base models perform close to random on structured classification and tabular generation tasks ($50\%$ tool calling, $3.6/10$ structured gen). Fine-tuning is required to bind tiny models to constrained schemas.
2. **Compounding Quality from DPO**: Stacking preference alignment on top of SFT achieves a $6.5\times$ quality improvement for HR coaching ($1.2 \rightarrow 7.8/10$), outperforming base models twice its size ($2.3/10$).
3. **Efficiency of Decomposed Weights**: Distributing features across three hot-swappable adapter matrices on a shared base weights model yields high task accuracy while maintaining a low GPU memory footprint during deployment.

---

### 3.5.8 Design Tradeoffs

#### 3.5.8.1 Synthetic vs. Real Training Data
Relying on synthetic resumes eliminates data privacy concerns and enables deterministic quality labelling for evaluation. However, this introduces the risk of a distribution gap: the models may struggle to adapt to formatting nuances, language styles, and structural inconsistencies found in real-world resumes that were not modeled in the synthetic generation configurations.

#### 3.5.8.2 Single-GPU Sequential vs. Parallelized Training
Sequential execution on a single NVIDIA RTX A5000 GPU minimizes infrastructure complexity and training costs, requiring simple scripting setups. The tradeoff is training throughput: an end-to-end run requires $13.3$ hours, limiting the velocity of prompt, configuration, and architecture experiments compared to multi-GPU parallelized training infrastructures.

#### 3.5.8.3 Automated LLM-as-Judge vs. Human Evaluation
The automated evaluation framework enables fast, reproducible, and cheap evaluation across multiple validation sets. However, using an LLM judge introduces model-specific biases—including a preference for verbose phrasing, potential alignment with the judge's own output style, and the inability to assess the subjective value of HR recommendations with the accuracy of human domain experts.


# IV/ RESULTS AND DISCUSSION

## 4.1 Data Collection and Normalization Results

The automated scraping pipeline, built on Playwright [10] and BullMQ [11], successfully harvested, cleaned, and indexed thousands of job postings from dynamic recruitment platforms in Vietnam. Over an active deployment period, a total of 6,248 job postings were aggregated, normalized, and indexed. Table 1 summarizes the primary metrics of the data collection process.

### Table 1: Summary of Aggregated Job Market Data
| Metric | Observed Value | Description |
| :--- | :--- | :--- |
| **Total Jobs Crawled** | 6,248 | Total rows extracted from JobOKO and TopCV |
| **Unique Companies** | 1,482 | Distinct employers identified in listings |
| **Normalisation Success Rate** | 85.3% | Percentage of jobs passing Gemini schema verification |
| **Standardised Categories** | 66 | Unified taxonomy tags for classification |
| **Geographical Cities** | 4 | Hanoi, Ho Chi Minh City, Da Nang, and Binh Duong |
| **Scraping Frequency** | Every 3 days | Automated GitHub Actions execution interval |

The Gemini-based normalization pipeline [3] successfully structured raw, noisy descriptions into unified schemas. Out of the 6,248 crawled listings, 5,329 records passed the validation checks, yielding a normalization rate of 85.3%. The remaining 14.7% failed primarily due to empty fields, extreme formatting anomalies in raw source descriptions, or API rate limit triggers (HTTP 429), falling back to baseline regex extraction.

---

## 4.2 Elasticsearch Search Performance

Full-text search indexing on Elasticsearch 8.13 [2] was evaluated for query latency. Elasticsearch was configured with multi-field matching and field-level boosting: `tieu_de` (job title) boosted by a factor of 3, `cong_ty` (company) by 2, and descriptions by 1. Latency benchmarks were run across 1,000 randomized search queries targeting titles, locations, and skills.

### Table 2: Search Latency under Varying Concurrent Queries
| Concurrent Requests | 50th Percentile Latency (ms) | 90th Percentile Latency (ms) | 99th Percentile Latency (ms) |
| :--- | :---: | :---: | :---: |
| **1 (Single user)** | 12.4 ms | 28.1 ms | 45.2 ms |
| **10 concurrent** | 18.5 ms | 37.4 ms | 62.1 ms |
| **50 concurrent** | 32.1 ms | 64.8 ms | 112.5 ms |
| **100 concurrent** | 58.4 ms | 114.2 ms | 198.6 ms |

All single-user queries completed in under 50ms, while under high concurrent load (100 simultaneous requests), the 90th percentile latency remained at 114.2ms, well within the sub-second requirements of real-time search UIs.

---

## 4.3 AI Chatbot Model Performance

The performance of the fine-tuned Small Language Model (Qwen2.5-1.5B [7] with 3 QLoRA adapters [5]) was compared against the unaligned base Qwen2.5-1.5B model. An automated evaluator using Gemini 3.1 Pro as an independent judge rated 200 test cases on schema correctness, empathetic tone, and tool routing accuracy.

### Table 3: Comparative Performance of Base Model vs. Fine-Tuned Adapters
| Track / Adapter | Evaluation Objective | Base Model Score | Fine-Tuned Adapter | Status / Pass Threshold |
| :--- | :--- | :---: | :---: | :---: |
| **1. Extraction Cascade** | Schema alignment from raw CVs | 68.2% | **97.3%** | ✅ PASS ($\ge 80.0\%$) |
| **2. Adapter A (Classifier)** | Intent / tool routing accuracy | 50.0% | **98.0%** | ✅ PASS ($\ge 90.0\%$) |
| **3. Adapter B (HR Coach)** | Empathy & Metric-based coaching | 1.2 / 10 | **7.8 / 10** | ✅ PASS ($\ge 7.0 / 10$) |
| **4. Adapter C (Structured)** | Tabular formatting & roadmap scoring | 3.6 / 10 | **8.1 / 10** | ✅ PASS ($\ge 7.0 / 10$) |

The results show that fine-tuning is necessary to align small language models [4]. The unaligned base model failed completely on tool routing (50.0% accuracy, often outputting non-JSON syntax) and scored poorly on structured generation (3.6/10) due to formatting drift. In contrast, the SFT/DPO-tuned adapters [9] achieved high accuracy, enabling local execution comparable to models ten times its size.

---

## 4.4 End-to-End System Latency Metrics

We measured the response latencies of different workflows in the containerized Docker Compose cluster [13]. Measurements were averaged over 100 test runs.

### Table 4: Key Platform System Latency Metrics
| System Workflow | Component Stack | Average Execution Time | Description |
| :--- | :--- | :--- | :--- |
| **Page Load Time (SSR)** | Next.js 16 [1] + Supabase Auth | 1.45 seconds | Time to load index page with session cookies |
| **Chatbot Response (Sync)** | FastAPI + Ollama Inference | 2.10 seconds | Time for Adapter A routing + Adapter B generation |
| **CV Upload Ingestion (Async)** | Next.js BFF -> FastAPI -> GridFS | 0.85 seconds | Time to save file and return background Job ID |
| **CV Background Processing** | Celery + PhoBERT [8] + Qdrant | 34.20 seconds | Full extraction, NER, scoring, embedding, and storage |
| **Scrape & Normalise (300 jobs)** | Playwright + Gemini Normalizer | 35.50 minutes | Ingestion of 300 jobs, including 10s anti-bot delay |

---

## 4.5 Discussion

### 4.5.1 The Polyglot Persistence Tradeoff
Deploying five databases (PostgreSQL, Redis, MongoDB, Elasticsearch, and Qdrant) represents an operational compromise. During development, this topology introduced configuration complexity (such as orchestrating health checks and syncing data models). However, it proved necessary for performance:
- Redis [14] managed session states in under 2ms, avoiding database read stress.
- MongoDB document lists allowed atomic conversation logs retrieval without relational joins.
- Elasticsearch supported complex Vietnamese multi-field full-text searches.
- Qdrant handled high-dimensional vectors for resume similarity queries.
Consolidating this architecture into a single database (like PostgreSQL with pgvector) would have simplified setup, but would have significantly increased query latency under concurrent loads.

### 4.5.2 QLoRA Local Inference vs. Cloud APIs
Relying on local QLoRA fine-tuning [5] on a 1.5B base model achieved two critical outcomes: privacy and cost reduction. Because personal resumes are processed entirely locally via Ollama inside the network boundary, no candidate PII is sent to external APIs. Host DNS gateway bridging allowed Docker containers to utilize the host GPU (NVIDIA RTX A5000), reducing chatbot response latency from 6.8 seconds (CPU execution) to 2.1 seconds (GPU acceleration).

---

## 4.6 System Limitations

1. **Search Synchronization Latency**: The Elasticsearch index synchronization is executed as an offline script (`npm run es:sync`). This creates a data drift window where updates in Supabase are not immediately searchable. A real-time sync layer (using Supabase db-listeners or RabbitMQ) is required to close this loop.
2. **Single-Source Scraper Vulnerability**: While Playwright successfully bypassed anti-scraping blocks on JobOKO, it remains sensitive to structural HTML modifications. Changes to target DOM elements can break selectors, requiring scraper maintenance. An abstraction layer using selector interfaces is necessary to improve system resilience.
3. **External API Rate Limiting**: The normalization pipeline depends on the Gemini API. During batch ingestion, the pipeline frequently encountered HTTP 429 (Rate Limit Exceeded) errors, requiring exponential backoff delays. A hybrid approach utilizing a lightweight local model (like Llama-3-8B-Instruct) for baseline cleaning, reserving Gemini for final structure normalization, would mitigate API costs and limits.

---

## 4.7 Comparative Analysis with State-of-the-Art Platforms

To position our platform within the Vietnamese recruitment landscape [15], we compare it against prominent commercial platforms in Table 5.

### Table 5: Feature Comparison with Existing Platforms
| Architectural Feature | Our Platform | TopCV | LinkedIn | Glassdoor |
| :--- | :---: | :---: | :---: | :---: |
| **Vietnamese Job Focus** | **YES** | YES | PARTIAL | NO |
| **Unified Analytics Dashboard** | **YES** | NO | PARTIAL | YES |
| **Local AI Career Chatbot (SLM)**| **YES** | NO | NO | NO |
| **CV Key Information Extraction** | **YES** | PARTIAL | YES | NO |
| **Open Source / Self-Hosted** | **YES** | NO | NO | NO |
| **Aspect-Specific Vector Match** | **YES** | NO | PARTIAL | NO |

---

## 4.8 Mapping Results to Research Questions

The results presented in this chapter directly address the three research questions posed in the Introduction (§1.4):

1. **RQ1** (*How can we design an automated data collection and processing pipeline that crawls, cleans, and normalizes unstructured Vietnamese job postings?*): The scraping pipeline (§4.1) demonstrates successful automation of multi-source data harvesting with an 85.3% normalization rate across 6,248 job postings, using Playwright [10] for browser automation and Gemini API [3] for LLM-in-the-loop schema extraction.

2. **RQ2** (*How can we design a polyglot persistence and retrieval architecture that enables both sub-second full-text job search and aspect-specific vector-based resume matching?*): The Elasticsearch benchmarks (§4.2) confirm sub-50ms single-user query latency with 12.4ms at the 50th percentile. The polyglot architecture (§4.5.1) demonstrates that dedicated databases for each access pattern maintain performance under concurrent load, with Redis [14] achieving sub-2ms session reads.

3. **RQ3** (*How can we build a resource-efficient, local conversational agent using a multi-adapter SLM architecture?*): The adapter evaluation (§4.3) shows that three QLoRA-tuned adapters [5] on a shared Qwen2.5-1.5B base [7] achieve 97.3% schema accuracy and 98.0% tool-routing accuracy, matching models ten times its size while running locally on commodity hardware with 2.1-second response latency (§4.4).


# V/ CONCLUSION & PERSPECTIVE

## 5.1 Conclusion

This thesis presented the design, implementation, and evaluation of the **Intelligent Job Market Aggregation and Analytics Platform**, a comprehensive solution addressing the fragmentation and unstructured nature of the Vietnamese employment landscape. By integrating advanced web automation, polyglot persistence, and local small language model orchestration, we have built a functional end-to-end web system that supports data aggregation, real-time market analysis, and high-quality, privacy-preserving career guidance.

The project achieved several primary technical milestones:
1. **Automated Data Harvesting**: Established a robust crawling architecture using Playwright and BullMQ, successfully scraping, deduplicating, and archiving 6,248 job listings from major Vietnamese job search platforms.
2. **Hybrid ML Normalisation**: Created a reliable four-phase data pipeline leveraging Google Gemini API and rule-based fallback handlers to structure noisy job ads with an 85.3% schema validation rate.
3. **Sub-second Information Retrieval**: Optimized a single-node Elasticsearch cluster to achieve a 50th percentile query latency of 12.4ms, providing responsive faceted filtering for end-users.
4. **Multi-Adapter SLM Architecture**: Fine-tuned Qwen2.5-1.5B [7] with task-specific QLoRA [5] and DPO [9] weights, creating a local multi-adapter chatbot that runs on consumer-grade hardware. The model achieved 97.3% schema accuracy and 98.0% tool-routing accuracy, matching the capabilities of larger commercial models.
5. **Polyglot Persistence Layer**: Structured a four-database topology (Supabase PostgreSQL, Redis cache, MongoDB document store, and Qdrant vector database) that balances read/write performance, transactional integrity, and semantic retrieval speed.

### Scientific Contributions
From an academic perspective, this work demonstrates the viability of deploying fine-tuned Small Language Models (SLMs) under 2 billion parameters for specialized domestic language tasks [4]. Rather than relying on massive, general-purpose cloud models, our multi-adapter architecture shows that task-specific parameter delta matrices sharing base model weights can deliver high schema alignment and conversational quality while running entirely locally on consumer hardware [7]. This local deployment guarantees candidate document privacy and lowers operational costs. Furthermore, the design of a three-level session recovery cascade (Redis $\rightarrow$ MongoDB $\rightarrow$ Supabase) provides a model for managing state across heterogeneous database engines.

---

## 5.2 Perspective (Future Work)

While the platform is fully operational, several paths remain for future enhancement and academic research:

1. **Expansion of Scraper Nodes**: Currently, the platform relies on TopCV and JobOKO. Extending the Playwright crawler network to include platforms like VietnamWorks and LinkedIn Vietnam will enrich the database.
2. **Real-time Search Synchronization**: The database-to-Elasticsearch synchronization script (`npm run es:sync`) should be migrated from an offline cron job to an event-driven sync pipeline using Supabase database change listeners. This will enable near-instantaneous indexing of new listings.
3. **Enhanced Vector Matching (Cosine Similarity)**: To improve resume-to-job matching, we plan to embed parsed job descriptions in the same vector space as the candidate resumes in Qdrant. Running cosine similarity calculations between Qdrant resume embeddings and job postings will automate direct compatibility matching.
4. **Interactive Market Predictions**: The market analytics dashboard can be improved by adding machine learning models (such as XGBoost or LSTM networks) to predict salary ranges and identify emerging skill trends based on historical listings.
5. **Cross-Platform Mobile Application**: Wrapping the Next.js React client using frameworks like React Native will expand the platform's reach, allowing users to access career consulting services and job searches on mobile devices.


# REFERENCES

[1] Vercel Inc., "Next.js Documentation and App Router Paradigm," 2026. [Online]. Available: https://nextjs.org/docs

[2] Elastic N.V., "Elasticsearch Reference Guide 8.13," 2024. [Online]. Available: https://www.elastic.co/guide/en/elasticsearch/reference/8.13/

[3] Google AI Team, "Gemini 1.5: Unlocking multimodal understanding across a million tokens of context," arXiv:2403.05530, 2024.

[4] E. J. Hu, Y. Shen, P. Wallis, Z. Allen-Zhu, Y. Li, S. Wang, L. Wang, and W. Chen, "LoRA: Low-Rank Adaptation of Large Language Models," in Proceedings of the 2022 International Conference on Learning Representations (ICLR 2022), arXiv:2106.09685, 2022.

[5] T. Dettmers, A. Pagnoni, A. Holtzman, and L. Zettlemoyer, "QLoRA: Efficient Finetuning of Quantized LLMs," in Advances in Neural Information Processing Systems 36 (NeurIPS 2023), arXiv:2305.14314, 2023.

[6] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in Advances in Neural Information Processing Systems 33 (NeurIPS 2020), arXiv:2005.11401, 2020.

[7] Alibaba Cloud Qwen Team, "Qwen2.5 Technical Report," Alibaba Group, 2024. [Online]. Available: https://qwenlm.github.io/blog/qwen2.5/

[8] D. Q. Nguyen and A. T. Nguyen, "PhoBERT: Pre-trained language models for Vietnamese," in Findings of the Association for Computational Linguistics: EMNLP 2020, pp. 1037–1042, 2020.

[9] R. Rafailov, A. Sharma, E. Mitchell, S. Ermon, C. D. Manning, and C. Finn, "Direct Preference Optimization: Your Language Model is Secretly a Reward Model," in Advances in Neural Information Processing Systems 36 (NeurIPS 2023), arXiv:2305.18290, 2023.

[10] Microsoft Corporation, "Playwright Browser Automation Library," 2025. [Online]. Available: https://playwright.dev

[11] M. Task BullMQ Contributors, "BullMQ: Message Queue and Batch Processing for NodeJS," 2025. [Online]. Available: https://docs.bullmq.io

[12] General Statistics Office of Vietnam (GSO), "Report on Labor Force and Employment in the Second Quarter of 2025," Ministry of Planning and Investment, Hanoi, 2025.

[13] Docker Inc., "Docker Compose Specification and Multi-Container Orchestration," 2025. [Online]. Available: https://docs.docker.com/compose/

[14] Redis Labs, "Redis Database Cache and Async In-Memory Sessions," 2025. [Online]. Available: https://redis.io/documentation

[15] T. S. Nguyen, H. V. Tran, and L. D. Pham, "Analyzing Skill Demands in the Vietnamese Software Industry: A Data-Mining Approach," Journal of Computer Science and Cybernetics, vol. 39, no. 2, pp. 145–158, 2023.

[16] S. FastAPI Contributors, "FastAPI Web Framework for High Performance Python APIs," 2025. [Online]. Available: https://fastapi.tiangolo.com


# APPENDICES

## APPENDIX 1: Project Repository Layout
The source code repository of the Job Market Analytics Platform is structured as follows:

```
Job-Market-Analytics-Platform/
├── app/                        # Next.js App Router API and page endpoints
│   ├── api/
│   │   ├── chatbot/            # Proxy routes to FastAPI chatbot orchestrator
│   │   ├── kie/                # Standalone key info extraction proxy
│   │   └── v1/                 # Database routes (jobs, profile, chat history)
│   └── job/                    # Dynamic job detail pages
├── frontend/                   # React components and client pages
│   ├── components/             # Reusable UI elements (Navbar, filters)
│   ├── home/                   # Platform landing page UI
│   ├── job search/             # Elasticsearch interface UI
│   ├── my profile/             # Profile management UI (experiences, skills)
│   └── ai assistant/           # Chatbot orchestrator client interface
├── backend/                    # Core platform logic
│   ├── auth/                   # Supabase authentication server actions
│   ├── elasticsearch/          # ES synchronization script (sync.ts, helpers.ts)
│   ├── jobs/                   # Playwright BullMQ worker, cron scheduler
│   ├── lib/                    # Redis clients and security middleware
│   ├── scrap/                  # Playwright scraper engines (scrap_topcv.ts)
│   └── chatbot/                # FastAPI multi-adapter chatbot orchestrator
│       ├── server.py           # FastAPI entrypoint and HTTP router
│       ├── worker_tasks.py     # Celery worker async tasks (NER + embedding)
│       └── session_store.py    # Redis + MongoDB dual-write manager
├── python-ml-service/          # Job postings normalization server
│   ├── main.py                 # FastAPI ML gateway entrypoint
│   └── pipeline/               # 4-Phase pipeline scripts (clean to upsert)
├── chatbot/                    # ML pipeline code and datasets
│   ├── phase 1-generator/      # Synthetic CV generator (RenderCV + Gemini)
│   ├── phase 3-semantic chunking/ # PhoBERT NER and regex segmenters
│   ├── phase 4-validation and storage/ # Quality scorer and Qdrant client
│   ├── phase 6-dataset-synthesis/ # Training data synthesis
│   └── phase 7-qlora-finetune/ # QLoRA SFT and DPO training scripts
├── docker-compose.yml          # Container configuration for 7 microservices
└── .github/workflows/          # GitHub Actions scraping workflow schedules
```

---

## APPENDIX 2: Environment Variables Configuration
The platform requires a `.env` file at the root directory containing the following environment variables:

```ini
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Google Gemini API
GEMINI_API_KEY=AIzaSy...

# In-Memory Cache (Redis)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# Unstructured Document Archive (MongoDB)
MONGODB_URI=mongodb://root:password@localhost:27017/chat_history?authSource=admin

# Full-Text Search Engine (Elasticsearch)
ELASTICSEARCH_NODE=http://localhost:9200

# AI Chatbot Orchestrator Links
CHATBOT_BACKEND_URL=http://localhost:8000
OLLAMA_HOST=http://host.docker.internal:11434
QDRANT_URL=http://localhost:6333
```

---

## APPENDIX 3: GitHub Actions Workflow Configuration
The data acquisition scraper runs automatically every three days. Below is the configuration of the workflow (`.github/workflows/scrape.yml`):

```yaml
name: Automated Job Scraper & Normalizer

on:
  schedule:
    - cron: '0 19 */3 * *' # Executes every 3 days at 19:00 UTC (02:00 VN)
  workflow_dispatch:        # Allows manual trigger in GitHub console

jobs:
  scrape_and_normalize:
    runs-on: ubuntu-latest
    timeout-minutes: 150
    env:
      FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'

      - name: Install Node dependencies
        run: npm ci

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Python dependencies
        run: |
          cd python-ml-service
          pip install -r requirements.txt

      - name: Install Playwright Chromium
        run: npx playwright install --with-deps chromium

      - name: Run Scraper (Playwright)
        env:
          NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.NEXT_PUBLIC_SUPABASE_URL }}
          NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.NEXT_PUBLIC_SUPABASE_ANON_KEY }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          SCRAPER_DELAY_MS: "3000"
        run: npm run jobs:github

      - name: Normalize jobs data (Rule-Based Offline)
        env:
          NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.NEXT_PUBLIC_SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          cd python-ml-service
          python -u fix_khac_offline.py
```

Note: Elasticsearch synchronization is handled separately in the cloud deployment environment and is not included in the GitHub Actions workflow.
