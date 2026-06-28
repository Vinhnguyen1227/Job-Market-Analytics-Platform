# II/ OBJECTIVE AND LITERATURE REVIEW

## 2.1 Research Objectives

The primary objective of this research is to design, implement, and evaluate an intelligent, end-to-end Job Market Aggregation and Analytics Platform that automates the collection and standardization of Vietnamese job listings, combines high-performance full-text search with real-time market analytics, and deploys a local, privacy-preserving AI career assistant powered by a multi-adapter Small Language Model (SLM). To achieve this, we propose a modular architecture comprising automated multi-source web scraping [10], heuristic-driven data normalization, sub-100ms Elasticsearch retrieval [2], and three task-specific QLoRA adapters [4,5] on a shared Qwen2.5-1.5B base model [7], orchestrated within a containerized polyglot persistence infrastructure [12,13].

---

## 2.2 Literature Review

### 2.2.1 Web Scraping and Data Normalization in HR Tech
Web scraping is a standard method for aggregating employment data in research and industry. Traditional crawlers rely on libraries like BeautifulSoup or Scrapy. However, modern job portals increasingly utilize Single Page Application (SPA) architectures and anti-bot defenses (such as dynamic DOM rendering, rate limits, and browser fingerprinting). This has shifted the state-of-the-art toward automated browser frameworks like Playwright [10] and Puppeteer, which run headless Chromium instances to simulate human interactions. 

Once scraped, the raw text remains unstructured and noisy. Standard normalization techniques rely on rule-based regular expressions and heuristic natural language processing parsing frameworks to clean salary formats, categorize locations, and extract job schemas. These rule-based parsing approaches offer highly predictable, deterministic transformations, making them ideal for high-throughput, low-latency ingestion pipelines. For Vietnamese text processing, an Electra-based pre-trained model (specifically NlpHUST's ner-vietnamese-electra-base [8]) enables domain-specific NER on Vietnamese documents, extracting named entities (persons, organizations, locations) that complement rule-based approaches. Server-side orchestration of these cleaning and processing pipelines is increasingly handled by high-performance Python API frameworks such as FastAPI [15].

### 2.2.2 Full-Text Search and Vector Retrieval
To navigate large-scale job databases, efficient search engines are required. Lucene-based search clusters, notably Elasticsearch, serve as the standard for full-text search [2]. They support multi-field querying, BM25 text relevance scoring, and faceted filter aggregations, enabling sub-second search times across millions of records. 

However, keyword search is limited by semantic vocabulary mismatch (e.g., searching "Frontend" might miss "React developer"). This has led to the adoption of vector-based similarity search using dense embeddings (e.g., BGE-M3, Sentence-BERT) indexed in specialized vector databases like Qdrant, following the Retrieval-Augmented Generation (RAG) paradigm [6]. In this platform, only resume documents are encoded as high-dimensional vectors in Qdrant to enable aspect-scoped semantic matching and skill-gap calculations, whereas job descriptions are indexed directly in Elasticsearch (full-text search) and matched via keyword/token overlap rather than job vector indexing.

### 2.2.3 Parameter-Efficient Fine-Tuning and SLMs
Although giant LLMs (e.g., GPT-4, Llama-3-70B) demonstrate impressive capabilities, deploying them in production presents severe challenges. They require costly, high-end cloud GPU infrastructure, introduce data privacy concerns, and exhibit high latency. Consequently, there is growing academic interest in Small Language Models (SLMs) with under 3 billion parameters, such as Qwen2.5-1.5B [7] or Gemma-2B, which can run locally on consumer-grade hardware.

To match the task performance of larger models, SLMs are adapted using Parameter-Efficient Fine-Tuning (PEFT) techniques, particularly Low-Rank Adaptation (LoRA) and its quantized variant, QLoRA [4]. QLoRA quantizes the base model's weights into 4-bit representation to minimize memory footprint, injecting lightweight trainable low-rank adapters. Direct Preference Optimization (DPO) further aligns model outputs with specific human guidelines (such as consulting tone and formatting constraints) by optimizing directly on pairwise preferences, bypassing the complexity of reinforcement learning with human feedback (RLHF) [9].
