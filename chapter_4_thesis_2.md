# Chapter 4: Full-Text Search Engine (Elasticsearch)

## 4.1 Search Architecture & Rationale

Building a job search system requires the ability to handle complex text queries, faceted filtering, and fast response times. In the initial phase, a relational database system (PostgreSQL via Supabase) was used as the primary data source. However, as the data volume grew and search requirements became more complex, this architecture revealed several limitations:

- **Limitations of SQL**: Full-text search queries or `ILIKE` operators in PostgreSQL are not optimized for natural language search, especially when handling spelling errors and relevance scoring.
- **Faceted Aggregations**: Dynamically calculating filter categories (e.g., counting the number of jobs per city or salary range) consumes a lot of resources if executed directly on SQL using complex `GROUP BY` clauses.

To resolve these issues, the system architecture adopts the Command Query Responsibility Segregation (CQRS) pattern:
- **Supabase (PostgreSQL)** acts as the "Source of Truth" (Transactional Database), storing the original data after scraping and normalization.
- **Elasticsearch 8.13** is used as a "Read-only Index" (Analytical Database), dedicated to processing search queries and filtering data for the frontend and AI Chatbot. The Elasticsearch system is deployed as a single-node cluster via Docker (`elasticsearch:8.13.0` on port 9200), ensuring lightning-fast search capabilities and multi-language support.

## 4.2 Index Schema & Mapping Strategies

To optimize Elasticsearch for both relevance scoring and exact filtering, the index structure (`jobs`) is meticulously designed within the data synchronization configuration file.

Two main data type strategies are used:
1. **Keyword Mapping**: Applied to fields that require exact match filtering and aggregations, such as `url`, `cities`, `categories`, `workTypes`, `levels`, `expBuckets`, and `salaryBuckets`. The `keyword` type allows Elasticsearch to build optimal data structures for directly searching original text structures.
2. **Text Mapping**: Applied to fields that require relevance scoring, such as `tieu_de` (job title) and `cong_ty` (company name), using the default `standard` analyzer.

**Optimizing the "Document Store" with `enabled: false`**:
Instead of extracting every detail of the job for indexing, the `raw_data` field is configured as an `object` type with the `enabled: false` option. This option instructs Elasticsearch to store the original JSON string of the job without indexing its internal contents.
This approach significantly saves system resources (RAM, CPU, disk space) during the indexing process while retaining all the data. When a search query returns results, the frontend can immediately retrieve detailed job data from `raw_data` without needing an additional query to Supabase for the information.

## 4.3 Data Ingestion & Deduplication Pipeline (Sync Flow)

Data is updated from Supabase to Elasticsearch via a batch synchronization pipeline. This process is triggered by a Node.js script (`sync.ts`).

1. **Batch Fetching**: The system fetches data from Supabase in paginated batches (500 records per batch) based on chronological order (`created_at`). Breaking the data down into batches helps prevent memory overflow.
2. **Memory-Resident Deduplication**: To avoid data duplication before pushing to Elasticsearch, an in-memory `Set` data structure (RAM) is used to track URLs that have already appeared (`seenUrls`). If the URL is missing, a composite key made from `tieu_de` and `cong_ty` is used as the identifier.
3. **Bulk API**: The deduplicated data is then converted into the ES Document format (via the `toEsDoc()` function) and pushed in bulk using the `_bulk` API. This execution method exponentially improves write speeds compared to sequentially writing individual documents using the `PUT` command. These operations are executed with the `refresh: true` option to ensure that new data is searchable immediately after the sync completes.

## 4.4 Vietnamese NLP & Heuristic Normalization Logic

Due to the unstructured nature of Vietnamese job postings, an internal library (`helpers.ts`) was built to extract and normalize data through Heuristic and Regex techniques prior to indexing:

- **Location Parsing**: Raw location strings (e.g., "Nơi làm việc: Hà Nội, Tp. HCM") are stripped of unnecessary prefixes, split by commas, and matched against a static array of 63 provinces/cities (`CITY_PATTERNS`). The system applies Regex for noise filtering when job title keywords (such as "chuyên viên", "trưởng phòng") are mistakenly identified as locations.
- **Salary Bucketing**: Foreign currency salaries (USD, JPY) are ignored. The system uses Regex to extract number ranges (e.g., "10 - 15 triệu"), removes commas, converts them to floating-point decimals representing millions of VND, and classifies them into fixed income ranges (0-3, 3-5, 5-10, 10-20, 20-50, Over 50 million).
- **Experience Parsing**: Text regarding experience (e.g., "dưới 1 năm", "trên 5 năm", or ranges like "1 - 2 năm") is scanned and normalized into a time range value in years. It is then assigned to static experience buckets (Under 1 year, 1-2 years, 2-5 years, Over 5 years).
- **Work Types**: English slang or mixed Vietnamese keywords (e.g., "full-time", "part-time", "thời vụ", "wfh") are mapped to standard tags such as "Toàn thời gian" (Full-time), "Bán thời gian" (Part-time), "Làm tại nhà" (Work from home).

## 4.5 Multi-Field Search & Relevance Tuning

When a search command is received from the AI Chatbot, the query is constructed via the Python async Elasticsearch client (`data_clients.py`) using the `bool` Query DSL.

1. **Relevance Scoring (Must Clause)**: If the user provides a `keyword`, the query uses the `multi_match` command with the `best_fields` option. The job title (`tieu_de`) is weighted with a multiplier of 3 (`^3`), while the company name (`cong_ty`) receives a weight multiplier of 2 (`^2`). The `fuzziness: AUTO` feature is enabled to tolerate minor spelling errors in Vietnamese.
2. **Strict Filtering (Filter Clauses)**: Optional parameters such as location, salary, and experience are passed in as `terms` filters, instructing the engine to strictly match the content against the defined `keyword` types.
3. **Salary Resolution**: When given an input range for desired salary (`min_salary` to `max_salary`), the algorithm automatically identifies salary buckets that overlap with the request and injects them into the query as a list of valid keywords.
4. **Client-side Highlight**: If a user searches by location, the returned payload within `raw_data` is automatically adjusted by moving the queried city to the top of the `cities` list, which helps the frontend interface and AI better assess visual priority.

## 4.6 Aggregation & Memory-Resident Enum Caching

To build a UI filtering experience or to provide a valid set of parameters for the AI Chatbot's Tool Calling process, the system needs to know the available filter values (e.g., which cities currently have job postings).

- **Elasticsearch Aggregations**: The client sends queries with a size of 0 (`size: 0`) requesting `terms aggregations` to group distinct attributes (`distinct_cities`, `distinct_categories`).
- **EnumCache Pattern**: To avoid constantly sending Aggregation queries that consume Elasticsearch resources, the `EnumCache` class (`enum_cache.py`) maintains these lists directly in the server's memory (RAM) with a Time-To-Live (TTL) of 3600 seconds (1 hour).
- **Async Background Refresh**: The cache refresh process runs as a background task via `asyncio.Task` (`_refresh_loop`). Therefore, any GET request from the frontend or Pydantic Validator from the Chatbot can retrieve these data tags in sub-millisecond times thanks to synchronous properties (`@property`), significantly improving the application's overall response speed.
