# System Patterns

## Architecture
* Next.js App Router at root.
* Components located under `./frontend/` folder, imported via `@/frontend/` alias.
* Auth & Supabase logic under `./backend/`.
* Independent python chatbot ML pipeline in `./chatbot/`.

## Key Patterns
* SSR: Server page routes in `./app/` fetch user/auth from `@/backend/supabase/server.ts`, pass to frontend page components.
* Client State: Local UI handling inside `@/frontend/` page files.
* Supabase SSR: Middleware in `./backend/supabase/middleware.ts` maintains sessions via HttpOnly cookies.

## Directory Layout
* `/app/`: Next.js page routing and server components.
* `/backend/`: Database, storage, and authentication.
* `/frontend/`: Visual presentation, dashboards, search views.
* `/chatbot/`: RAG pipeline and Python scripts.
