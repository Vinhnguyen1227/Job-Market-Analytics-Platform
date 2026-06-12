Chat Flow User type -> next-app BFF -> chatbot-api FastAPI POST /api/chat. FastAPI server.py check Redis session_store.py for session_id. Check slash_commands.py. If no slash -> intent_router.py send prompt to Adapter A (careerintel-tool-call) via Ollama. Adapter A output JSON tool + params. tool_dispatcher.py run tool:

search_jobs -> search elasticsearch:9200 -> format reply.
assess_resume -> check Redis resume_id -> Adapter B (careerintel-hr-coach).
match_jobs -> search qdrant:6333 -> Adapter B.
interview_prep -> search qdrant:6333 -> Adapter C (careerintel-structured-gen).
general_response -> Adapter B free chat. FastAPI append user + assistant message to Redis session:{session_id}:history. Return JSON -> BFF -> Frontend.
CV Upload Flow User upload file -> next-app BFF -> FastAPI POST /api/upload. FastAPI save temp file. FastAPI send process_cv_task to celery-worker via Redis broker. FastAPI write job_id to Redis job_tracker. Return job_id. Frontend poll GET /api/chatbot/status/{jobId}. Celery worker run Phase 3 (parse/NER) + Phase 4 (Qdrant upsert). Celery worker save resume_id + resume_dict to Redis session:{session_id}. Celery worker mark job COMPLETED. Frontend hydrate state.

Multiple Concurrent Users Flow FastAPI use async/await. Handle many HTTP requests no block. Frontend hold session_id. Pass session_id every API call. session_store.py isolate state in Redis:

session:{session_id} -> hold CV data (resume_id, resume_name).
session:{session_id}:history -> hold last 10 chat turns. User A never see User B data. State 100% separate. Heavy CV extract go to Celery queue. API stay fast. Celery workers process parallel. Ollama handle LLM generation. Concurrency depend on Ollama host GPU.