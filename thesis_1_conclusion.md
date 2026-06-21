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
