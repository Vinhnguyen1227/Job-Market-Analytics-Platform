# Active Context

## Active Goal
* Scrape pipeline split into async worker (Celery/Airflow).

## Current State
* Re-run build succeeded after resolving typescript issues (pdf-parse typings, explicit filter parameter type, and signup action return type alignment).
* Next.js development server running on `http://localhost:3000`.
* FastAPI chatbot backend running on `http://127.0.0.1:8000`.
* Codebase successfully re-indexed using GitNexus (`2,503` nodes, `4,105` edges, `60` clusters, `103` flows).
* Scraper Celery worker and Redis broker setup in `./scraper/` using Docker Compose. Ready for execution.

## Obstacles
* None. Everything builds, runs, and indexes smoothly.
