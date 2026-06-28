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
│   ├── jobs/                   # Playwright worker, cron scheduler
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
