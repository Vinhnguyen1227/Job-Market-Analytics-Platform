# IV/ RESULTS AND DISCUSSION

## 4.1 Data Collection and Normalization Results

The automated scraping pipeline, built on Playwright [10], successfully harvested, cleaned, and indexed thousands of job postings from dynamic recruitment platforms in Vietnam. Over an active deployment period, a total of 6,248 job postings were aggregated, normalized, and indexed. Table 1 summarizes the primary metrics of the data collection process.

### Table 1: Summary of Aggregated Job Market Data
| Metric | Observed Value | Description |
| :--- | :--- | :--- |
| **Total Jobs Crawled** | 6,248 | Total rows extracted from JobOKO and TopCV |
| **Unique Companies** | 1,482 | Distinct employers identified in listings |
| **Normalisation Success Rate** | 85.3% | Percentage of jobs passing rule-based validation verification |
| **Standardised Categories** | 66 | Unified taxonomy tags for classification |
| **Geographical Cities** | 4 | Hanoi, Ho Chi Minh City, Da Nang, and Binh Duong |
| **Scraping Frequency** | Every 3 days | Automated GitHub Actions execution interval |

The heuristic-based normalization pipeline successfully structured raw, noisy descriptions into unified schemas. Out of the 6,248 crawled listings, 5,329 records passed the validation checks, yielding a normalization rate of 85.3%. The remaining 14.7% failed primarily due to empty fields or extreme formatting anomalies in raw source descriptions, falling back to baseline regex extraction.

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

The results show that fine-tuning is necessary to align small language models [4]. The unaligned base model struggled with intent routing (50.0% accuracy, often failing JSON syntax constraints) and scored poorly on structured generation (3.6/10) due to formatting drift. In contrast, the SFT/DPO-tuned adapters [9] achieved high accuracy, enabling task-specific intent classification and schema formatting comparable to models ten times its size.

---

## 4.4 End-to-End System Latency Metrics

We measured the response latencies of different workflows in the containerized Docker Compose cluster [12]. Measurements were averaged over 100 test runs.

### Table 4: Key Platform System Latency Metrics
| System Workflow | Component Stack | Average Execution Time | Description |
| :--- | :--- | :--- | :--- |
| **Page Load Time (SSR)** | Next.js 16 [1] + Supabase Auth | 1.45 seconds | Time to load index page with session cookies |
| **Chatbot Response (Sync)** | FastAPI + Ollama Inference | 2.10 seconds | Time for Adapter A routing + Adapter B generation |
| **CV Upload Ingestion (Async)** | Next.js BFF -> FastAPI -> GridFS | 0.85 seconds | Time to save file and return background Job ID |
| **CV Background Processing** | Celery + Electra NER [8] + Qdrant | 34.20 seconds | Full extraction, NER, scoring, embedding, and storage |
| **Scrape & Normalise (300 jobs)** | Playwright + Heuristic Parser | 35.50 minutes | Ingestion of 300 jobs, including 10s anti-bot delay |

---

## 4.5 Discussion

### 4.5.1 The Polyglot Persistence Tradeoff
Deploying five databases (PostgreSQL, Redis, MongoDB, Elasticsearch, and Qdrant) represents an operational compromise. During development, this topology introduced configuration complexity (such as orchestrating health checks and syncing data models). However, it proved necessary for performance:
- Redis [13] managed session states in under 2ms, avoiding database read stress.
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

---

## 4.7 Comparative Analysis with State-of-the-Art Platforms

To position our platform within the Vietnamese recruitment landscape [14], we compare it against prominent commercial platforms in Table 5.

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

1. **RQ1** (*How can we design an automated data collection and processing pipeline that crawls, cleans, and normalizes unstructured Vietnamese job postings?*): The scraping pipeline (§4.1) demonstrates successful automation of multi-source data harvesting with an 85.3% normalization rate across 6,248 job postings, using Playwright [10] for browser automation and rule-based regular expressions and heuristic natural language processing for normalization.

2. **RQ2** (*How can we design a polyglot persistence and retrieval architecture that enables both sub-second full-text job search and aspect-specific vector-based resume matching?*): The Elasticsearch benchmarks (§4.2) confirm sub-50ms single-user query latency with 12.4ms at the 50th percentile. The polyglot architecture (§4.5.1) demonstrates that dedicated databases for each access pattern maintain performance under concurrent load, with Redis [13] achieving sub-2ms session reads.

3. **RQ3** (*How can we build a resource-efficient, local conversational agent using a multi-adapter SLM architecture?*): The adapter evaluation (§4.3) shows that three QLoRA-tuned adapters [5] on a shared Qwen2.5-1.5B base [7] achieve 97.3% schema accuracy and 98.0% tool-routing accuracy, matching the task-specific precision of models ten times its size while running locally on commodity hardware with 2.1-second response latency (§4.4).
