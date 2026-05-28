Please address the comments from this code review:

## Overall Comments
- The new async job model (FastAPI returns `job_id` from `/api/chat` and `/api/upload`) isn't wired into the `AIAssistantPage` yet: the frontend ignores `job_id` and never calls `/api/chatbot/status/[jobId]`, so long‑running tasks will only ever show the placeholder responses; consider adding a polling layer that replaces the interim message with the final result when the job completes.
- There is a response shape mismatch between `handleFileUpload` and the FastAPI `/api/upload` endpoint: the frontend expects `resume_id` and `resume_name` in the immediate response, but the backend only returns `success`, `job_id`, `session_id`, `message`, and `error`, so you should either change the frontend to treat this as a queued job (using the status endpoint) or extend the backend to return the fields the UI relies on.
- In `backend/chatbot/Dockerfile`, `COPY ../../chatbot /chatbot` will fail under the `chatbot-heavy/medium/light` Docker build context (`../backend/chatbot` in `docker-compose.yml`) because `../../chatbot` is outside the build context; you’ll need to either adjust the build context to include the top‑level `chatbot` directory or move those files under the existing context.

## Individual Comments

### Comment 1
<location path="app/api/kie/route.ts" line_range="13" />
<code_context>
+    }
+
+    // Step 1: Forward file to FastAPI
+    const fastApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
+    
+    // Create new FormData to forward
</code_context>
<issue_to_address>
**suggestion (bug_risk):** KIE API uses NEXT_PUBLIC_API_URL while chatbot APIs use CHATBOT_BACKEND_URL, leading to inconsistent backend configuration.

Using `NEXT_PUBLIC_API_URL` here while the chatbot routes use `CHATBOT_BACKEND_URL` creates two separate ways to configure the FastAPI backend. This increases the risk of staging/prod mismatches and unintentionally exposing internal URLs via a `NEXT_PUBLIC_*` env var. Consider using a single server-side env var for the FastAPI base URL and sharing it across all backend proxy routes.

Suggested implementation:

```typescript
    // Step 1: Forward file to FastAPI
    // Use the same server-side backend URL as the chatbot APIs for consistency
    const fastApiUrl = process.env.CHATBOT_BACKEND_URL || 'http://127.0.0.1:8000';

```

1. Verify that `CHATBOT_BACKEND_URL` is defined in your deployment environment (and `.env.local` for local dev) and points to the FastAPI backend.
2. For full consistency, consider extracting this base URL into a shared helper (e.g. `lib/backend.ts`) and using it across all proxy routes (including chatbot routes and this KIE route).
</issue_to_address>

### Comment 2
<location path="memory-bank/techContext.md" line_range="35" />
<code_context>
+  * **Phase 1-generator**: 15 symbols (cohesion: 91%)
+  * **Tasks**: 14 symbols (cohesion: 100%)
+  * **Auth**: 12 symbols (cohesion: 87%)
+  * **Ai assistant**: 7 symbols (cohesion: 92%)
+
</code_context>
<issue_to_address>
**nitpick (typo):** Capitalize "AI" in "Ai assistant" for consistency and correctness.

Change `**Ai assistant**` to `**AI assistant**` to align with standard capitalization and the rest of the document.

Suggested implementation:

```
  * **Auth**: 12 symbols (cohesion: 87%)
  * **AI assistant**: 7 symbols (cohesion: 92%)

```

In the current file, there is likely a line reading `* **Ai assistant**: 7 symbols (cohesion: 92%)` directly after the `Auth` line. If so, instead of inserting a new line as above, modify that existing line by replacing `**Ai assistant**` with `**AI assistant**` while keeping the rest of the line unchanged.
</issue_to_address>

### Comment 3
<location path="memory-bank/progress.md" line_range="10" />
<code_context>
+* [x] Launch development server (`npm run dev`)
+* [x] Launch chatbot backend (`uvicorn server:app --port 8000`)
+* [x] Index codebase with GitNexus and sync with Memory Bank
+* [x] Setup async scraper worker (Celery, Redis)
+* [x] Add ML async queue to FastAPI chatbot (Redis sessions, Celery workers, job polling)
+* [x] KIE Route migration to ML Async Queue (Python-based processing)
</code_context>
<issue_to_address>
**suggestion (typo):** Use "Set up" (verb) instead of "Setup" (noun) in this sentence.

Since it’s used as a verb here, it should be `Set up async scraper worker (Celery, Redis)`.

```suggestion
* [x] Set up async scraper worker (Celery, Redis)
```
</issue_to_address>

### Comment 4
<location path="memory-bank/activeContext.md" line_range="7" />
<code_context>
+* ML async queue added to FastAPI chatbot backend.
+
+## Current State
+* Re-run build succeeded after resolving typescript issues (pdf-parse typings, explicit filter parameter type, and signup action return type alignment).
+* Next.js development server running on `http://localhost:3000`.
+* FastAPI chatbot backend running on `http://127.0.0.1:8000`.
</code_context>
<issue_to_address>
**nitpick (typo):** Capitalize "TypeScript" correctly.

Please change `typescript issues` to `TypeScript issues` for correct capitalization.

```suggestion
* Re-run build succeeded after resolving TypeScript issues (pdf-parse typings, explicit filter parameter type, and signup action return type alignment).
```
</issue_to_address>

### Comment 5
<location path="plan.md" line_range="1" />
<code_context>
+Database split. Supabase = OLTP. Big data viz need OLAP (ClickHouse/BigQuery). Keep market trend queries fast.
+Component strictness. Server Components handle data fetch → fast FCP. Client Components handle glassmorphism + animations only.
\ No newline at end of file
</code_context>
<issue_to_address>
**suggestion (typo):** Correct subject-verb agreement in "Big data viz need OLAP".

Change the phrase to `Big data viz needs OLAP`.
</issue_to_address>

### Comment 6
<location path="apikey-scandocflow.txt" line_range="1" />
<code_context>
+NP8EEplfYryej80ceNHILaMs3E8niwnMYpITkgaRpSNPGXkHs3ChHADAqZJltm11
\ No newline at end of file
</code_context>
<issue_to_address>
**🚨 issue (security):** Avoid committing raw API keys or secrets to the repository.

This appears to be a real secret token. Remove it from version control and load it via environment variables or a secret manager instead. If it is valid, rotate the key after removing it from the repo.
</issue_to_address>