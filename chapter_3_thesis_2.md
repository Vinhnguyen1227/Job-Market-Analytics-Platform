# Chapter 3: Polyglot Persistence and Search Infrastructure

This chapter outlines the core data architecture of the Job Market Analytics Platform. Managing diverse data types—ranging from highly structured user profiles to massive, unstructured job postings—requires a specialized approach. The system adopts a polyglot persistence strategy, utilizing five distinct databases (Supabase, Redis, MongoDB, Elasticsearch, and Qdrant), each selected to optimally address specific data shapes and access patterns.

## 3.1 Polyglot Persistence Justification

The platform handles several distinct data workloads:
1.  **Relational Data:** User accounts, authentication, and structured relationships (e.g., user-to-job applications).
2.  **Search Data:** Millions of text-heavy job descriptions requiring complex full-text search and facet filtering.
3.  **Ephemeral/Cache Data:** High-speed session tokens, background job tracking, and frequent query results.
4.  **Unstructured Chat Data:** Dynamic, schema-less chatbot conversation logs (handled via MongoDB).
5.  **Vector Data:** Semantic embeddings for AI-driven skill matching (handled via Qdrant).

A traditional, monolithic database approach would struggle to balance these conflicting requirements (e.g., fast text search vs. strict relational integrity). By deploying specialized databases, the system achieves optimal performance, scalability, and maintainability. This chapter focuses on the core platform components: Supabase, Redis, and Elasticsearch.

## 3.2 Supabase (Core Relational Database)

Supabase, built on top of PostgreSQL, serves as the primary relational database for the application's core logic.

### Structured Entities
Supabase is responsible for managing structured entities that require strong ACID (Atomicity, Consistency, Isolation, Durability) guarantees. This includes user authentication profiles, account settings, and primary metadata for job postings. The relational model ensures data integrity and enforces complex business rules through foreign key constraints and database triggers.

## 3.3 Redis (Session and Cache Management)

Redis is deployed as the high-speed, in-memory cache layer, critical for reducing latency and offloading repetitive tasks from the primary databases.

### Singleton Connection
Within the application, Redis connections are managed via a singleton pattern (`new Redis(process.env.REDIS_URL)`). This ensures efficient connection pooling and minimizes the overhead of establishing new TCP connections for every request.

### Core Caching Workloads
-   **Authentication Management:** Redis is used for token blacklisting, ensuring that revoked JWTs are immediately invalidated across the distributed system.
-   **Job Tracking:** Background processing tasks (e.g., data scraping queues managed by BullMQ) rely on Redis to track job state and progress rapidly.
-   **Query Caching:** Frequently accessed, compute-intensive data (like trending skills or aggregate market statistics) are cached in Redis to improve dashboard load times.

## 3.4 Elasticsearch (Full-Text Search Engine)

To power the core "job search" functionality, the system relies on Elasticsearch. Standard relational databases are not optimized for unstructured text search at scale.

### Data Synchronization
Job posting data is continuously synchronized from the primary Supabase database into Elasticsearch. This ensures the search index remains up-to-date while decoupling read-heavy search traffic from the transactional database.

### Advanced Mapping and Indexing
Elasticsearch indices are carefully mapped to support diverse search requirements:
-   **Keyword Mapping:** Fields requiring exact matches and aggregations (facets)—such as locations, job levels, and specific skill tags—are mapped as `keyword` types. This allows the frontend to quickly generate filter sidebars and facet counts.
-   **Text Mapping:** Large text blocks, specifically the job title (`tieu_de`) and job description, are mapped as `text`. The system applies standard text analyzers (including tokenization and lowercasing) to these fields, enabling robust full-text search, typo tolerance, and relevance scoring (TF-IDF/BM25).
