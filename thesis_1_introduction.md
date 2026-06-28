# I/ INTRODUCTION

## 1.1 Global Context & Motivation

In recent years, the rapid growth of the digital economy has transformed the global and domestic labor markets. Vietnam, as a fast-emerging market, has experienced a significant surge in demand for high-skilled labor, particularly in information technology, digital marketing, and financial services [11]. However, the domestic job market remains highly fragmented. Job postings are scattered across dozens of disconnected online employment portals (such as TopCV, VietnamWorks, and JobOKO), each using proprietary classifications, diverse salary formatting, and varying descriptions. This fragmentation creates search friction for job seekers who must manually browse multiple websites, compile matching data, and evaluate their own qualifications against inconsistent requirement definitions.

For students and young professionals entering this dynamic landscape, the challenge is twofold. First, they lack centralized, real-time analytics to understand broader market demands—such as which skills are most sought after, how salaries are distributed across regions, or which sectors are expanding. Second, they lack access to personalized, expert career guidance. Traditional career consulting is either prohibitively expensive or generic, while existing automated resume screening tools (often based on basic keyword matching) fail to provide actionable, constructive feedback for candidates to improve their resumes and bridge skill gaps.

This research is motivated by the potential of combining web automation, information retrieval, and modern artificial intelligence to build a unified, intelligent analytics platform. By combining automated data aggregation with local large language model (LLM) inference, we can create a system that not only indexes and visualizes market trends in real time but also serves as an interactive, resume-aware career assistant. Such a platform democratizes career guidance, helping candidates optimize their market readiness.

---

## 1.2 Problem Statement

Despite these advancements, existing Vietnamese career portals and recruitment tools exhibit three main technical limitations:

1. **Fragmented and Unstructured Data Sources**: Web-scraped data from Vietnamese job sites is extremely noisy, with unstructured salary ranges, non-standardized skill names, and duplicate postings [14]. Traditional classification algorithms and regex-based heuristics often struggle to structure Vietnamese job postings accurately due to syntax complexity, spelling variations, and mixed English-Vietnamese terminology.
2. **High Resource Demands for Intelligent Chatbots**: Deploying interactive, conversational career agents usually requires querying expensive, external cloud APIs or hosting massive models. This introduces high API dependencies and operating costs that can restrict accessibility for local educational or public organizations, and poses privacy risks when processing personal Curriculum Vitae (CV) documents.
3. **Task Drift in Single-Prompt SLMs**: A single parameter-efficient small language model (SLM) under 2 billion parameters struggles to generalize across multiple heterogeneous tasks (e.g., intent classification, prose coaching, structured data formatting) within a single prompt context, resulting in format drift and loss of coherence.

---

## 1.3 Research Questions

To address these limitations, this thesis investigates the following key research questions:

1. **RQ1**: How can we design an automated data collection and processing pipeline that crawls, cleans, and normalizes unstructured Vietnamese job postings into a high-quality standardized schema using rule-based regular expressions and heuristic natural language processing?
2. **RQ2**: How can we design a polyglot persistence and retrieval architecture that enables both high-performance, low-latency full-text job search and aspect-specific vector-based resume matching?
3. **RQ3**: How can we build a resource-efficient, local conversational agent using a multi-adapter SLM architecture that matches the task-specific schema extraction and intent routing accuracy of larger commercial LLMs while running on commodity hardware?

---

## 1.4 Scientific and Technical Contributions

This thesis makes three primary scientific and technical contributions to the field of intelligent recruitment aggregation and local AI coaching:

1. **Automated Data Normalization**: We design and implement an end-to-end data acquisition and normalization pipeline tailored for the Vietnamese job market, utilizing Playwright for robust dynamic crawling and a hybrid extraction framework that achieves an 85.3% validation rate.
2. **Polyglot Persistence Layer**: We construct a production-ready polyglot persistence layer (combining MongoDB, Redis, Elasticsearch, and Qdrant) that manages caching, session history, full-text faceted search, and resume vector embeddings, maintaining sub-50ms query latency under loads of up to 100 concurrent requests.
3. **Multi-Adapter Local Inference**: We propose a resource-efficient local conversational agent based on a multi-adapter SLM architecture. By fine-tuning task-specific QLoRA adapters on Qwen2.5-1.5B and applying DPO alignment, we show that a lightweight model can run locally on consumer hardware while matching the task-specific performance of commercial models ten times its size.
