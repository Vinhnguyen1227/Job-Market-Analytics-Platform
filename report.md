# REPORT.MD — Ke hoach viet Bao cao Khoa luan Tot nghiep ICT
## Intelligent Job Market Aggregation and Analytics Platform

> **Template chuan**: USTH ICT Bachelor Thesis 2026
> **Cau truc**: Chia thanh 9 STEP doc lap de Gemini thuc hien tuan tu
> **Output**: Moi step tao ra 1 file markdown rieng → ghep lai thanh bao cao hoan chinh

---

## TONG QUAN DU AN (Context cho Gemini)

**Ten de tai**: Intelligent Job Market Aggregation and Analytics Platform
**Sinh vien**: Nguyen Vinh (Vinhnguyen1227)
**Truong**: University of Science and Technology of Hanoi (USTH), Khoa ICT

### Stack cong nghe da xay dung:
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS 4, Lucide React
- **Backend**: Next.js API Routes, Server Actions, Supabase (Auth + PostgreSQL)
- **Search Engine**: Elasticsearch 8.13 (full-text search qua hang nghin tin tuyen dung)
- **AI/ML**: Google Gemini API (normalization pipeline), QLoRA fine-tuned Qwen2.5-1.5B (chatbot voi 3 adapter)
- **Scraping**: Playwright + BullMQ + TypeScript (cao JobOKO, TopCV)
- **Data Normalization**: FastAPI + Python 4-phase pipeline (clean → semantic → hash → upsert)
- **Databases**: PostgreSQL (Supabase), MongoDB (chat history), Redis (cache/queue), Qdrant (vector DB)
- **Infrastructure**: Docker Compose, GitHub Actions CI/CD, Celery workers

### Tinh nang da hoan thanh:
1. He thong xac thuc (Supabase Auth, SSR cookies, middleware)
2. Trang tim kiem viec lam (Elasticsearch full-text, bo loc nganh nghe/dia diem/muc luong)
3. Dashboard Market Insights (bieu do xu huong thi truong, phan phoi luong)
4. AI Chatbot (Qwen2.5-1.5B + 3 LoRA adapter: tool-call, HR-coach, structured-gen)
5. Pipeline cao du lieu tu dong (GitHub Actions moi 3 ngay)
6. Pipeline chuan hoa du lieu AI (Gemini-powered 4-phase normalization)
7. Trang ho so nguoi dung + CV upload/KIE (Key Info Extraction)

---

## STEP 1 — COVER PAGE & FRONT MATTER
**File output**: `report/01_front_matter.md`

Nhiem vu cua Gemini: Tao file report/01_front_matter.md theo dung format USTH, bao gom:

1. **Cover page** (trang bia):
   - University: University of Science and Technology of Hanoi (USTH)
   - Department: Department of Information and Communication Technology
   - Thesis title: "Intelligent Job Market Aggregation and Analytics Platform"
   - Student name: [de trong — sinh vien tu dien]
   - External Supervisor: [de trong]
   - Internal Supervisor: [de trong]
   - Year: Hanoi, June 2026

2. **Supervisor Certification** (trang xac nhan cua giang vien huong dan):
   - Form template theo chuan USTH 2025-2026

3. **Table of Contents** (Muc luc):
   ```
   ACKNOWLEDGEMENTS
   LIST OF ABBREVIATIONS
   LIST OF TABLES
   LIST OF FIGURES
   ABSTRACT
   I/ INTRODUCTION
   II/ OBJECTIVES
   III/ MATERIALS AND METHODS
   IV/ RESULTS AND DISCUSSION
   V/ CONCLUSION & PERSPECTIVE
   REFERENCES
   APPENDICES
   ```

4. **ACKNOWLEDGEMENTS** (Loi cam on):
   - Viet noi dung loi cam on chuyen nghiep (~150 tu tieng Anh)
   - Cam on: giang vien huong dan, USTH, ban be/gia dinh
   - De cap den viec xay dung he thong phan tich thi truong viec lam

5. **LIST OF ABBREVIATIONS**:
   - API: Application Programming Interface
   - BullMQ: Bull Message Queue
   - CI/CD: Continuous Integration / Continuous Deployment
   - ES: Elasticsearch
   - JWT: JSON Web Token
   - KIE: Key Information Extraction
   - LoRA: Low-Rank Adaptation
   - LLM: Large Language Model
   - ML: Machine Learning
   - NLP: Natural Language Processing
   - OCR: Optical Character Recognition
   - QLoRA: Quantized Low-Rank Adaptation
   - RAG: Retrieval-Augmented Generation
   - SLM: Small Language Model
   - SSR: Server-Side Rendering
   - USTH: University of Science and Technology of Hanoi

6. **LIST OF TABLES** (placeholder — dien so trang sau):
   - Table 1: Technology stack overview
   - Table 2: Database systems and their roles
   - Table 3: ML pipeline phases summary
   - Table 4: System performance metrics
   - Table 5: Comparison with existing platforms
   - Table 6: Chatbot adapter performance

7. **LIST OF FIGURES** (placeholder):
   - Figure 1: Overall system architecture diagram
   - Figure 2: Data collection pipeline flow
   - Figure 3: AI normalization pipeline (4 phases)
   - Figure 4: Chatbot architecture (3 adapters)
   - Figure 5: Job search interface screenshot
   - Figure 6: Market insights dashboard screenshot
   - Figure 7: Elasticsearch indexing flow

---

## STEP 2 — ABSTRACT
**File output**: `report/02_abstract.md`

Nhiem vu cua Gemini: Viet ABSTRACT dung chuan USTH (khong qua 250 tu tieng Anh + 6 keywords).

Noi dung can de cap:
- Context: Thi truong viec lam Viet Nam, thieu nen tang phan tich du lieu tong hop
- Muc tieu: Xay dung nen tang web tong hop, tim kiem, va phan tich tin tuyen dung
- Phuong phap:
  - Web scraping tu dong (Playwright, BullMQ, GitHub Actions)
  - AI normalization pipeline 4 phases (Gemini API)
  - Full-text search (Elasticsearch)
  - AI chatbot voi SLM (Qwen2.5-1.5B + 3 LoRA adapters)
- Ket qua: 6,000+ tin tuyen dung da chuan hoa, tim kiem sub-second, chatbot ho tro nghe nghiep
- Ket luan: Dong gop cho viec hieu thi truong lao dong Viet Nam

Keywords (6 tu):
job market analytics, web scraping, Elasticsearch, large language model, fine-tuning, Vietnam labor market

---

## STEP 3 — INTRODUCTION (Section I)
**File output**: `report/03_introduction.md`

Nhiem vu cua Gemini: Viet Section I: INTRODUCTION (khoang 2-3 trang, tieng Anh hoc thuat).

Cau truc:

### 1.1 Global Context & Motivation
- Thi truong viec lam Viet Nam dang tang truong manh, thieu cong cu phan tich tong hop
- Cac nen tang hien tai (TopCV, LinkedIn, Joboko) roi rac, khong co phan tich thi truong
- Nhu cau cua sinh vien/nguoi di lam trong viec hieu xu huong nganh

### 1.2 Literature Review
- He thong tong hop viec lam (job aggregator): Indeed, Glassdoor
- Ung dung NLP trong phan tich tin tuyen dung
- Cac phuong phap web scraping cho du lieu HR
- Chatbot tu van nghe nghiep voi LLM

### 1.3 Problem Statement
- Lack of centralized, real-time job market analytics for Vietnam
- No intelligent CV-aware career assistant in Vietnamese context
- Scraped data quality issues (inconsistent formatting, duplicates)

### 1.4 Research Questions
1. How to efficiently aggregate and normalize job postings from multiple Vietnamese sources?
2. How to provide meaningful market analytics from scraped job data?
3. How to build a resource-efficient AI career assistant using fine-tuned SLMs?

---

## STEP 4 — OBJECTIVES (Section II)
**File output**: `report/04_objectives.md`

Nhiem vu cua Gemini: Viet Section II: OBJECTIVES (ngan gon, 2-3 doan van tieng Anh).

Scientific Objective:
Design and implement an end-to-end intelligent job market analytics platform that:
(1) automates data collection from Vietnamese job portals,
(2) normalizes raw scraped data using LLM-powered pipelines,
(3) enables sub-second full-text search and real-time market analytics,
(4) provides personalized career guidance through a fine-tuned small language model chatbot.

Specific Goals:
1. Build automated web scraping pipeline for Vietnamese job sources (JobOKO, TopCV)
2. Implement AI-powered 4-phase normalization (Gemini API + rule-based fallback)
3. Deploy Elasticsearch-based full-text search over 6,000+ job records
4. Fine-tune Qwen2.5-1.5B with QLoRA (3 specialized adapters)
5. Build interactive market insights dashboard with salary/industry/location analytics
6. Deploy containerized production-ready infrastructure (Docker Compose, 7 services)

---

## STEP 5 — MATERIALS AND METHODS (Section III)
**File output**: `report/05_methods.md`

Nhiem vu cua Gemini: Viet Section III: MATERIALS AND METHODS (khoang 4-5 trang, tieng Anh hoc thuat).
Day la phan dai va ky thuat nhat. Trinh bay theo paragraphs, KHONG phai bullet points.

Cau truc:

### 3.1 System Architecture
Mo ta kien truc tong quan (tham khao system_design.md):
- 4 layers: Presentation → Application → Data → Infrastructure
- Polyglot persistence strategy (PostgreSQL, Elasticsearch, MongoDB, Redis, Qdrant)
- Communication: REST API, SSE streaming, WebSocket
- Bao gom Figure 1: System Architecture Diagram (mo ta so do bang van ban)

### 3.2 Technology Stack
Trinh bay bang Table 1: Technology Stack
Cac cot: Layer | Technology | Purpose
Cac hang:
- Frontend: Next.js 16, React 19, TypeScript - SSR web application
- Styling: Tailwind CSS 4, Lucide React - Responsive UI
- Auth: Supabase Auth, @supabase/ssr - Cookie-based SSR authentication
- Search: Elasticsearch 8.13 - Full-text job search
- Scraping: Playwright, BullMQ, TypeScript - Automated data collection
- Normalization: FastAPI, Gemini API, Python - AI-powered data cleaning
- Chatbot: Qwen2.5-1.5B, QLoRA, Ollama - Fine-tuned career assistant
- Queue: Redis, BullMQ, Celery - Task queue & caching
- Storage: Supabase PG, MongoDB, Qdrant - Multi-model persistence
- Infra: Docker Compose, GitHub Actions - Containerization & CI/CD

### 3.3 Data Collection Pipeline
Chi tiet pipeline cao du lieu:
- Cong nghe: Playwright headless browser, vuot SPA anti-bot
- Nguon du lieu: JobOKO (vn.joboko.com), TopCV
- BullMQ job queue: cron scheduling, retry logic
- GitHub Actions: tu dong chay moi 3 ngay
- Rate limiting: 7-giay delay giua cac request
- Output: raw job records → Supabase PostgreSQL
- Bao gom Figure 2: Data Collection Flow Diagram

### 3.4 AI Normalization Pipeline (4 Phases)
Trinh bay Table 2: ML Pipeline Phases va Figure 3:
- Phase 1 (phase1_clean.py): Text cleaning, remove HTML/noise
- Phase 2 (phase2_semantic.py): Gemini API: extract salary, skills, job type, location
- Phase 3 (phase3_hash.py): SHA-256 deduplication hash (company+title+location+month)
- Phase 4 (phase4_upsert.py): Upsert to Supabase PostgreSQL on url conflict

### 3.5 Search Engine Implementation
- Elasticsearch 8.13, single-node deployment
- Index mapping: title, company, location, salary, nganh_nghe_chuan_hoa (66 standardized tags)
- Query: multi-match voi boosting (title^3, company^2, description^1)
- Filters: location, salary range, job type, industry tag
- sync.ts script: Supabase → Elasticsearch sync (backend/elasticsearch/sync.ts)

### 3.6 AI Chatbot Architecture
Trinh bay Figure 4: Chatbot Architecture:
- Base model: Qwen2.5-1.5B (Small Language Model)
- Fine-tuning: QLoRA (Quantized Low-Rank Adaptation)
- 3 specialized adapters:
  - Adapter A (Tool-Call Router): Routes user intent → JSON {tool, params}
  - Adapter B (HR Coach): Generates Vietnamese career feedback
  - Adapter C (Structured Gen): Creates roadmaps, interview Q&A tables
- Deployment: Ollama local inference, Docker container
- RAG: Qdrant vector DB cho CV context (KIE pipeline)
- Session management: Redis 24h TTL
- Async tasks: Celery workers

### 3.7 Authentication System
- Supabase Auth voi cookie-based sessions (HttpOnly, SSR-safe)
- Next.js middleware: tu dong refresh session moi request
- Server Actions: login, signup, logout (backend/auth/actions.ts)
- JWT blacklisting: Redis

### 3.8 Infrastructure & Deployment
- Docker Compose: 7 services (redis, mongodb, elasticsearch, qdrant, next-app, chatbot-api, celery-worker)
- Health checks tren tat ca services (redis ping, mongosh ping, ES cluster health)
- GitHub Actions CI/CD: tu dong scrape + normalize moi 3 ngay

---

## STEP 6 — RESULTS (Section IV, Part A)
**File output**: `report/06_results.md`

Nhiem vu cua Gemini: Viet Section IV: RESULTS (khoang 3-4 trang, tieng Anh hoc thuat).

Cau truc:

### 4.1 Data Collection Results
- 6,000+ job records collected from JobOKO and TopCV
- Ty le chuan hoa thanh cong: khoang 85% qua Gemini pipeline
- Phan phoi dia ly: Ha Noi, TP.HCM, Da Nang, can ten thi thanh khac
- Table 3: Summary of collected data
  (Cac metric: Total jobs indexed / Unique companies / Cities covered / Industry categories / Scraping frequency)

### 4.2 Search Performance
- Elasticsearch query latency: duoi 100ms (sub-second)
- Full-text search tren keyword tim kiem
- Figure 5: Job Search Interface Screenshot (mo ta UI)
- Filter performance: location, salary range, industry tag

### 4.3 AI Normalization Quality
- So sanh truoc/sau normalization: raw text vs structured data
- Ty le extraction chinh xac cho: salary range, job type, skills
- Fallback: rule-based khi Gemini API rate-limit (429 error)

### 4.4 Market Insights Dashboard
- Figure 6: Market Insights Dashboard Screenshot
- Bieu do: top industries, salary distribution, location heatmap
- Xu huong: top in-demand skills (IT, marketing, finance)

### 4.5 AI Chatbot Results
- Response quality cua 3 adapters
- Table 4: Chatbot Adapter Performance
  (Cac cot: Adapter | Task | Response Quality)
  - Tool-Call Router | Intent classification | High accuracy JSON output
  - HR Coach | CV feedback | Vietnamese empathetic tone
  - Structured Gen | Roadmap/Interview Q | Structured Markdown output
- KIE pipeline: CV parsing accuracy
- Session management: Redis 24h TTL working

### 4.6 System Performance
- Table 5: System Metrics
  - Page load time (SSR): < 2s
  - Elasticsearch query: < 100ms
  - Chatbot response (sync): < 3s
  - Scrape cycle (300 jobs): approximately 35 minutes
  - Docker startup time: approximately 60s (Elasticsearch)

---

## STEP 7 — DISCUSSION (Section IV, Part B)
**File output**: `report/07_discussion.md`

Nhiem vu cua Gemini: Viet phan DISCUSSION (khoang 2 trang, tieng Anh hoc thuat).

Cau truc:

### 4.7 Discussion of Results

Thanh cong:
- Polyglot persistence strategy: moi database phu hop voi dac diem du lieu
- QLoRA fine-tuning cho phep chay chatbot tren hardware thuong (khong can GPU cloud)
- Playwright + BullMQ vuot qua SPA anti-bot tot hon scrapy truyen thong

Han che & Phan tich:
1. Data drift: ES sync phai chay thu cong → stale search results
   - Nguyen nhan: sync khong duoc tich hop vao GitHub Actions pipeline
   - Giai phap de xuat: Supabase webhooks real-time sync

2. Scraping single-source dependency: chi JobOKO duoc cao day du
   - Nguyen nhan: moi site can scraper rieng, anti-bot phuc tap
   - Giai phap: ScraperInterface abstraction layer

3. Profile data anti-pattern: kinh nghiem/hoc van luu trong user_metadata thay vi proper tables
   - Tac dong: bloat JWT tokens, khong query duoc
   - Giai phap: migrate sang profiles, experiences, educations tables

4. Gemini rate limiting: 429 errors khi normalize batch lon
   - Giai phap de xuat: exponential backoff + sleep(1) between calls

So sanh voi state-of-the-art:
Table 6: Comparison with existing platforms
Cac cot: Feature | This Platform | TopCV | LinkedIn | Glassdoor
Cac hang:
- Vietnamese job focus: YES / YES / PARTIAL / NO
- Market analytics dashboard: YES / NO / PARTIAL / YES
- AI career chatbot (SLM): YES / NO / NO / NO
- CV KIE pipeline: YES / PARTIAL / YES / NO
- Open source / self-hosted: YES / NO / NO / NO

---

## STEP 8 — CONCLUSION & PERSPECTIVE (Section V)
**File output**: `report/08_conclusion.md`

Nhiem vu cua Gemini: Viet Section V: CONCLUSION & PERSPECTIVE (khoang 1 trang, tieng Anh hoc thuat).

Cau truc:

### 5.1 Conclusion
Tom tat cac thanh tuu chinh:
1. Da xay dung thanh cong end-to-end job market analytics platform
2. Automated data pipeline: 6,000+ records, cap nhat moi 3 ngay
3. Sub-second full-text search qua Elasticsearch
4. AI-powered normalization voi Gemini API (4-phase pipeline)
5. Fine-tuned SLM chatbot (Qwen2.5-1.5B + 3 QLoRA adapters)
6. Containerized deployment voi Docker Compose (7 services)

Dong gop khoa hoc:
- Chung minh tinh kha thi cua QLoRA fine-tuning cho career domain tieng Viet
- Thiet ke polyglot persistence architecture cho job aggregation
- Pipeline chuan hoa du lieu HR ket hop LLM + rule-based fallback

### 5.2 Perspective (Future Work)
Huong phat trien tiep theo:
1. Multi-source scraping: Mo rong sang LinkedIn, VietnamWorks, CareerViet
2. Real-time ES sync: Supabase webhooks → instant search update
3. Social login: Google/LinkedIn OAuth via Supabase
4. CV matching: semantic similarity giua CV va JD (Qdrant cosine similarity)
5. Mobile app: React Native wrapper
6. Staging environment: Vercel preview deployments
7. Analytics improvements: salary prediction model, skill gap analysis

---

## STEP 9 — REFERENCES & APPENDICES
**File output**: `report/09_references_appendices.md`

Nhiem vu cua Gemini: Viet REFERENCES va APPENDICES theo chuan USTH.

### REFERENCES
Liet ke it nhat 15 tai lieu tham khao theo format so trong ngoac vuong [N].
Format vi du:
[1] Vercel Inc., "Next.js Documentation," 2024. [Online]. Available: https://nextjs.org/docs
[2] Elastic N.V., "Elasticsearch Reference Guide 8.13," 2024. [Online]. Available: https://www.elastic.co/guide/en/elasticsearch/reference/8.13/
[3] E.J. Hu, Y. Shen, P. Wallis et al., "LoRA: Low-Rank Adaptation of Large Language Models," in Proceedings of ICLR 2022, arXiv:2106.09685, 2022.
[4] T. Dettmers, A. Pagnoni, A. Holtzman, L. Zettlemoyer, "QLoRA: Efficient Finetuning of Quantized LLMs," in Advances in NeurIPS 36 (NeurIPS 2023), arXiv:2305.14314, 2023.
[5] P. Lewis, E. Perez, A. Piktus et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in Advances in NeurIPS 33 (NeurIPS 2020), arXiv:2005.11401, 2020.

Cac nguon con lai can tim kiem them (Gemini tu tim va dien):
- Qwen2.5 technical report (Alibaba Cloud, 2024)
- Playwright documentation (Microsoft)
- BullMQ documentation
- Vietnamese job market reports (GSO - Tong cuc Thong ke)
- Web scraping ethics and legality papers
- Supabase documentation
- Docker documentation
- Redis documentation
- FastAPI documentation
- Elasticsearch for information retrieval: relevant academic papers

### APPENDICES

Appendix A: Project Repository Structure
```
Job-Market-Analytics-Platform/
├── app/                    # Next.js App Router (pages & API routes)
├── frontend/               # UI page components
├── backend/
│   ├── auth/               # Supabase auth Server Actions
│   ├── elasticsearch/      # ES sync scripts (sync.ts, helpers.ts)
│   ├── jobs/               # BullMQ queue, cron, github_action.ts
│   ├── lib/                # Redis, security utilities
│   ├── scrap/              # Playwright scrapers (scrap_topcv.ts)
│   └── chatbot/            # FastAPI chatbot API
├── python-ml-service/
│   ├── main.py             # FastAPI normalization gateway
│   └── pipeline/           # phase1-4 Python scripts
├── chatbot/                # KIE pipeline (phase 3-4 RAG)
├── docker-compose.yml      # Full stack (7 services)
└── .github/workflows/      # GitHub Actions CI/CD
```

Appendix B: Environment Variables Required
```
NEXT_PUBLIC_SUPABASE_URL      - Supabase project URL
NEXT_PUBLIC_SUPABASE_ANON_KEY - Supabase anonymous key
SUPABASE_SERVICE_ROLE_KEY     - Admin key (server-only)
GEMINI_API_KEY                - Google Gemini API key (server-only)
REDIS_URL / REDIS_PASSWORD    - Redis connection
MONGODB_URI                   - MongoDB connection
ELASTICSEARCH_NODE            - Elasticsearch HTTP endpoint
CHATBOT_BACKEND_URL           - FastAPI chatbot service URL
OLLAMA_HOST                   - Ollama inference server
QDRANT_URL                    - Qdrant vector database URL
```

Appendix C: GitHub Actions Workflow Summary
- Trigger: cron 0 0 */3 * * (every 3 days at midnight)
- Steps: checkout → npm install → playwright scrape → python normalize → es:sync
- Runner: ubuntu-latest, 2 vCPUs

---

## HUONG DAN GHEP FILE CHO GEMINI

Sau khi hoan thanh tat ca 9 steps, ghep theo thu tu:
```
report/01_front_matter.md
report/02_abstract.md
report/03_introduction.md
report/04_objectives.md
report/05_methods.md
report/06_results.md
report/07_discussion.md
report/08_conclusion.md
report/09_references_appendices.md
```
Output cuoi cung: report/FINAL_REPORT.md

---

## LUU Y QUAN TRONG CHO GEMINI

1. Ngon ngu: Toan bo viet bang tieng Anh hoc thuat (academic English), formal tone
2. Format: Dung markdown headers (# ## ###) tuong ung voi cau truc thesis
3. Do dai: Moi section it nhat du noi dung nhu yeu cau (khong viet qua ngan)
4. Citations: Dung so trong ngoac vuong [1], [2]... theo chuan USTH
5. Tables & Figures: Luon co introduction paragraph truoc table/figure
6. Khong bia so lieu: Cac so lieu cu the (latency, accuracy %) chi dien neu co trong codebase; neu khong biet thi viet "approximately" hoac [TBD]
7. Tham chieu code: Khi de cap den implementation, co the reference file path (vd: backend/elasticsearch/sync.ts)
