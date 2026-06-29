# Progress

## Milestones
* [x] Initialize Memory Bank
* [x] Install dependencies (`npm install`)
* [x] Verify Next.js build (`npm run build`)
* [x] Launch development server (`npm run dev`)
* [x] Launch chatbot backend (`uvicorn server:app --port 8000`)
* [x] Index codebase with GitNexus and sync with Memory Bank
* [x] Set up async scraper worker (Celery, Redis)
* [x] Add ML async queue to FastAPI chatbot (Redis sessions, Celery workers, job polling)
* [x] KIE Route migration to ML Async Queue (Python-based processing)
* [x] Draft and compile all missing sections of Thesis 1 (Abstract, Intro, Objectives, Results, Conclusion, References, Appendices) conforming to 2026 USTH template
* [x] Generate LaTeX format `thesis_1.tex` with all 15 figures and custom style mappings, verified for syntax and escaping correctness.
* [x] Manually verify all table values, apply style fixes (author name diacritics, duplicate caption prefixes, remove emojis), delete generation scripts, and compile final PDF with Tectonic.
* [x] Create `thesis_mismatches_fix_guide.md` to document exact replacement instructions for five factual mismatches and style/formatting corrections in `thesis_1.tex`.
* [x] Apply mismatches and style fixes from guide to `thesis_1.tex` and compile final PDF using Tectonic.
* [x] Fix table text sizes to 12pt, left-align cells, resolve page margin overflows (Tables 3, 4, 6, 7), and unify typewriter fonts in `thesis_1.tex`.
* [x] Rename enlarged text diagrams in G Drive folder `G:\My Drive\thesis_images\sua thesis 1 part 2` to standard format.
* [x] Convert all tables to `tabularx` to make them exactly match the page layout width (`\textwidth`).
* [x] Replace all local diagrams in `thesis_1_images` with the new versions from `G:\My Drive\thesis_images\sua thesis 1 part 2`.
* [x] Restructure Chapters 1, 2, 4, 5 of Thesis 1 (move Literature Review to Chapter 2, tone down overclaims, add Contributions).
* [x] Restructure Section 3.5.1 pipeline flow to text description and remove section numbers from figure captions in Thesis 1.
* [x] Move ACKNOWLEDGEMENTS and LIST OF ABBREVIATIONS before Table of Contents, remove redundant title repetition from figure captions, and add colons format in Thesis 1.
* [x] Change hyperlink fonts in LaTeX references to Times New Roman by setting urlstyle to same in Thesis 1.
* [x] Remove unused abbreviations (CI/CD, GHA, USTH) from List of Abbreviations in Thesis 1.
* [ ] Add interactive slash command suggestion chips in the chatbot frontend page.
* [x] Remove all emojis from chatbot frontend and backend files.


## Bug Log
* **Turbopack build failed**: `Module not found: Can't resolve '@supabase/ssr'`.
  * **Fix**: Ran `npm install` to restore packages. Verified.
* **TypeScript missing declarations for pdf-parse**:
  * **Fix**: Installed `@types/pdf-parse` as a devDependency. Verified.
* **Implicit any in KIE route**:
  * **Fix**: Explicitly cast `word` parameter to `any` in `filter` function. Verified.
* **No overload matches useActionState in signup**:
  * **Fix**: Aligned return type of `signup` action in `backend/auth/actions.ts` to always return both `error` and `success` fields (either string or null). Verified.
