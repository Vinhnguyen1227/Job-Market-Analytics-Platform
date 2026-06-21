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
