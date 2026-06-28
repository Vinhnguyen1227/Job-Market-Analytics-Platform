# Guide: Fix Factual Mismatches and Style in thesis_1.tex

This guide provides instructions and exact string replacements to fix factual mismatches and apply formatting/style corrections to `thesis_1.tex`.

---

## PART 1: FACTUAL MISMATCHES

### Mismatch 1: Section 1.2.2 (Full-Text Search and Vector Retrieval)
Clarify that only resumes are encoded as vectors in Qdrant, while job descriptions are indexed in Elasticsearch and matched via keyword/token overlap, not job description vector indexing.

#### Line 247
**Before:**
```latex
However, keyword search is limited by semantic vocabulary mismatch (e.g., searching ``Frontend'' might miss ``React developer''). This has led to the adoption of vector-based similarity search using dense embeddings (e.g., BGE-M3, Sentence-BERT) indexed in specialized vector databases like Qdrant, following the Retrieval-Augmented Generation (RAG) paradigm [\hyperlink{cite6}{6}]. By encoding resumes and job descriptions as high-dimensional vectors, platforms can perform aspect-scoped semantic matching and skill-gap calculations, capturing semantic relationships that keyword matching misses.
```

**After:**
```latex
However, keyword search is limited by semantic vocabulary mismatch (e.g., searching ``Frontend'' might miss ``React developer''). This has led to the adoption of vector-based similarity search using dense embeddings (e.g., BGE-M3, Sentence-BERT) indexed in specialized vector databases like Qdrant, following the Retrieval-Augmented Generation (RAG) paradigm [\hyperlink{cite6}{6}]. In this platform, only resume documents are encoded as high-dimensional vectors in Qdrant to enable aspect-scoped semantic matching and skill-gap calculations, whereas job descriptions are indexed directly in Elasticsearch (full-text search) and matched via keyword/token overlap rather than job vector indexing.
```

---

### Mismatch 2: PhoBERT to Electra NER replacement
Change "PhoBERT" to "Electra-based model" (specifically `NlpHUST/ner-vietnamese-electra-base`) where NER is mentioned, including references.

#### Occurrence 2.1 (Line 238)
**Before:**
```latex
For Vietnamese text processing, pre-trained language models such as PhoBERT [\hyperlink{cite8}{8}] enable domain-specific NER on Vietnamese documents, extracting named entities (persons, organizations, locations) that complement rule-based approaches.
```

**After:**
```latex
For Vietnamese text processing, an Electra-based pre-trained model (specifically NlpHUST's ner-vietnamese-electra-base [\hyperlink{cite8}{8}]) enables domain-specific NER on Vietnamese documents, extracting named entities (persons, organizations, locations) that complement rule-based approaches.
```

#### Occurrence 2.2 (Line 346)
**Before:**
```latex
It executes the same three-stage extraction cascade used in the training pipeline (semantic chunking $\rightarrow$ regex extraction $\rightarrow$ PhoBERT NER), followed by quality scoring and BGE-M3 embedding generation.
```

**After:**
```latex
It executes the same three-stage extraction cascade used in the training pipeline (semantic chunking $\rightarrow$ regex extraction $\rightarrow$ Electra NER), followed by quality scoring and BGE-M3 embedding generation.
```

#### Occurrence 2.3 (Line 946)
**Before:**
```latex
    \item Phase 2: Extraction Cascade: Parses resumes and structures them into a canonical resume schema using regex and PhoBERT NER.
```

**After:**
```latex
    \item Phase 2: Extraction Cascade: Parses resumes and structures them into a canonical resume schema using regex and Electra NER.
```

#### Occurrence 2.4 (Line 996)
**Before:**
```latex
Regex rules extract deterministic formats (emails, phone numbers, GPA, URLs, date ranges), while a pre-trained PhoBERT model extracts contextual entities such as organization names, locations, and candidate names.
```

**After:**
```latex
Regex rules extract deterministic formats (emails, phone numbers, GPA, URLs, date ranges), while a pre-trained Electra-based model (ner-vietnamese-electra-base) extracts contextual entities such as organization names, locations, and candidate names.
```

#### Occurrence 2.5 (Line 1239 - in Table 4 / Table 8 in updated guide)
**Before:**
```latex
    \textbf{CV Background Processing} & Celery + PhoBERT [\hyperlink{cite8}{8}] + Qdrant & 34.20 seconds & Full extraction, NER, scoring, embedding, and storage \\
```

**After:**
```latex
    \textbf{CV Background Processing} & Celery + Electra NER [\hyperlink{cite8}{8}] + Qdrant & 34.20 seconds & Full extraction, NER, scoring, embedding, and storage \\
```

#### Occurrence 2.6 (Line 1391 - Reference 8)
**Before:**
```latex
\hypertarget{cite8}{}[8] D. Q. Nguyen and A. T. Nguyen, ``PhoBERT: Pre-trained language models for Vietnamese,'' in \textit{Findings of the Association for Computational Linguistics: EMNLP 2020}, pp. 1037--1042, 2020.
```

**After:**
```latex
\hypertarget{cite8}{}[8] NlpHUST, ``ner-vietnamese-electra-base model,'' Hugging Face Hub, 2022. [Online]. Available: \url{https://huggingface.co/NlpHUST/ner-vietnamese-electra-base}
```

---

### Mismatch 3: Section 4.2 (Elasticsearch Search Performance)
Remove claim that job descriptions are boosted/searched in Elasticsearch index. Only title and company are searched and boosted.

#### Line 1171
**Before:**
```latex
Full-text search indexing on Elasticsearch 8.13 [\hyperlink{cite2}{2}] was evaluated for query latency. Elasticsearch was configured with multi-field matching and field-level boosting: \tieu\_de (job title) boosted by a factor of 3, \cong\_ty (company) by 2, and descriptions by 1. Latency benchmarks were run across 1,000 randomized search queries targeting titles, locations, and skills.
```

**After:**
```latex
Full-text search indexing on Elasticsearch 8.13 [\hyperlink{cite2}{2}] was evaluated for query latency. Elasticsearch was configured with multi-field matching and field-level boosting: \tieu\_de (job title) boosted by a factor of 3 and \cong\_ty (company) by 2. Descriptions are not searched or boosted in the search index. Latency benchmarks were run across 1,000 randomized search queries targeting titles, locations, and skills.
```

---

### Mismatch 4: Table 4 (CV Background Processing)
*(Already handled under Mismatch 2, Occurrence 2.5).*

---

### Mismatch 5: Section 4.1 (Geographical Cities)
Clarify that system supports 64+ cities, but offline normalization script maps Hanoi, Ho Chi Minh, and Da Nang with aliases.

#### Line 1164
**Before:**
```latex
The heuristic-based normalization pipeline successfully structured raw, noisy descriptions into unified schemas. Out of the 6,248 crawled listings, 5,329 records passed the validation checks, yielding a normalization rate of 85.3\%. The remaining 14.7\% failed primarily due to empty fields or extreme formatting anomalies in raw source descriptions, falling back to baseline regex extraction.
```

**After:**
```latex
The heuristic-based normalization pipeline successfully structured raw, noisy descriptions into unified schemas. Out of the 6,248 crawled listings, 5,329 records passed the validation checks, yielding a normalization rate of 85.3\%. The remaining 14.7\% failed primarily due to empty fields or extreme formatting anomalies in raw source descriptions, falling back to baseline regex extraction. Although the database schema and indexing layer support 64+ Vietnamese cities, the offline normalization script maps input variations specifically to the primary commercial hubs (Hanoi, Ho Chi Minh City, and Da Nang) along with their common aliases to ensure strict geographic standardization.
```

---
---

## PART 2: FORMATTING & STYLE CORRECTIONS

### Fix 1: Times New Roman Font
Set the global font to Times New Roman.

#### Line 11 (Preamble)
**Before:**
```latex
\usepackage{fancyhdr} % For bottom-right page numbers
```

**After:**
```latex
\usepackage{fancyhdr} % For bottom-right page numbers
\usepackage{newtxtext,newtxmath}
```

---

### Fix 2: Disable Italics Globally
Disable all inline italics (`\textit`, `\itshape`, and `\it`) globally.

#### Line 38 (Right before \begin{document})
**Before:**
```latex
}
```

**After:**
```latex
}

% Disable italics globally
\renewcommand{\textit}[1]{\textup{#1}}
\renewcommand{\itshape}{\upshape}
\let\it\textup
```

---

### Fix 3: Remove Parentheses from Headings
Delete parenthetical phrases from headings and Table of Contents entries.

#### 3.1 Heading 1.2.3 (Line 250-251)
**Before:**
```latex
\addcontentsline{toc}{subsection}{1.2.3 Parameter-Efficient Fine-Tuning (PEFT) and SLMs}
\noindent{\Large \textbf{1.2.3 Parameter-Efficient Fine-Tuning\\(PEFT) and SLMs}\par}
```

**After:**
```latex
\addcontentsline{toc}{subsection}{1.2.3 Parameter-Efficient Fine-Tuning and SLMs}
\noindent{\Large \textbf{1.2.3 Parameter-Efficient Fine-Tuning and SLMs}\par}
```

#### 3.2 Heading 3.3 (Line 604-605)
**Before:**
```latex
\addcontentsline{toc}{section}{3.3 Frontend AI Presentation Layer (Next.js)}
\noindent{\LARGE \textbf{3.3 Frontend AI Presentation Layer (Next.js)}\par}
```

**After:**
```latex
\addcontentsline{toc}{section}{3.3 Frontend AI Presentation Layer}
\noindent{\LARGE \textbf{3.3 Frontend AI Presentation Layer}\par}
```

#### 3.3 Heading 5.2 (Line 1352-1353)
**Before:**
```latex
\addcontentsline{toc}{section}{5.2 Perspective (Future Work)}
\noindent{\LARGE \textbf{5.2 Perspective (Future Work)}\par}
```

**After:**
```latex
\addcontentsline{toc}{section}{5.2 Perspective}
\noindent{\LARGE \textbf{5.2 Perspective}\par}
```

---

### Fix 4: Enlarge Table Text Size and Fix Wrapping
Remove `\resizebox` scaling (which makes text too small), add `\large` to all tables, and adjust columns to wrap text dynamically using fixed `p{width}` column types where text is long.

#### 4.1 CV Processing Stages (Line 458-474)
**Before:**
```latex
\begin{table}[H]
    \centering
    \caption[CV Processing Stages]{\textbf{CV Processing Stages}}
    \vspace{0.2cm}
    \resizebox{\textwidth}{!}{
    \begin{tabular}{l|l|l|l}
    \hline\hline
    Stage & Input & Output & Transformation \\
    \hline
    \textbf{Ingestion} & Binary file (PDF/DOCX/Image) & Raw bytes on shared volume & Format validation, zero-copy exchange \\
    \textbf{Text Extraction} & Raw bytes & Unstructured text string & PyMuPDF parsing or Tesseract OCR fallback \\
    \textbf{Semantic Structuring} & Flat text & \texttt{CanonicalResume} typed JSON & Section splitting $\rightarrow$ chunking $\rightarrow$ entity extraction $\rightarrow$ merge \\
    \textbf{Validation \& Vectorization} & Typed JSON & Quality-scored vectors in Qdrant & Multi-criteria scoring + BGE-M3 dense embeddings \\
    \hline\hline
    \end{tabular}
    }
\end{table}
```

**After:**
```latex
\begin{table}[H]
    \centering
    \caption[CV Processing Stages]{\textbf{CV Processing Stages}}
    \vspace{0.2cm}
    \large
    \renewcommand{\arraystretch}{1.3}
    \begin{tabular}{p{2.5cm} | p{3.5cm} | p{3.5cm} | p{5.5cm}}
    \hline\hline
    Stage & Input & Output & Transformation \\
    \hline
    \textbf{Ingestion} & Binary file (PDF/DOCX/Image) & Raw bytes on shared volume & Format validation, zero-copy exchange \\
    \textbf{Text Extraction} & Raw bytes & Unstructured text string & PyMuPDF parsing or Tesseract OCR fallback \\
    \textbf{Semantic Structuring} & Flat text & \texttt{CanonicalResume} typed JSON & Section splitting $\rightarrow$ chunking $\rightarrow$ entity extraction $\rightarrow$ merge \\
    \textbf{Validation \& Vectorization} & Typed JSON & Quality-scored vectors in Qdrant & Multi-criteria scoring + BGE-M3 dense embeddings \\
    \hline\hline
    \end{tabular}
\end{table}
```

#### 4.2 Tool Dispatch Strategies (Line 845-862)
**Before:**
```latex
\begin{table}[H]
    \centering
    \caption[Tool Dispatch Strategies]{\textbf{Tool Dispatch Strategies}}
    \vspace{0.2cm}
    \resizebox{\textwidth}{!}{
    \begin{tabular}{l|l|l|l}
    \hline\hline
    Tool Intent & Data Source & Primary Adapter & Core Output Modality \\
    \hline
    \texttt{search\_jobs} & Elasticsearch & None (Direct Query) & Structured Job Listing Cards \\
    \texttt{assess\_resume} & MongoDB (Resume JSON) & Adapter B (HR Coach) & Formatted Performance Prose \\
    \texttt{match\_jobs} & Qdrant (Vectors) & Adapter B (HR Coach) & Skill-Gap Analysis Narrative \\
    \texttt{interview\_prep} & MongoDB (Resume JSON) & Adapter C (Structured Gen) & Question-Rubric Tables / Roadmaps \\
    \texttt{general\_response} & MongoDB (Session History) & Adapter B (HR Coach) & Conversational Vietnamese Dialogue \\
    \hline\hline
    \end{tabular}
    }
\end{table}
```

**After:**
```latex
\begin{table}[H]
    \centering
    \caption[Tool Dispatch Strategies]{\textbf{Tool Dispatch Strategies}}
    \vspace{0.2cm}
    \large
    \renewcommand{\arraystretch}{1.3}
    \begin{tabular}{p{3cm} | p{3.5cm} | p{3cm} | p{5.5cm}}
    \hline\hline
    Tool Intent & Data Source & Primary Adapter & Core Output Modality \\
    \hline
    \texttt{search\_jobs} & Elasticsearch & None (Direct Query) & Structured Job Listing Cards \\
    \texttt{assess\_resume} & MongoDB (Resume JSON) & Adapter B (HR Coach) & Formatted Performance Prose \\
    \texttt{match\_jobs} & Qdrant (Vectors) & Adapter B (HR Coach) & Skill-Gap Analysis Narrative \\
    \texttt{interview\_prep} & MongoDB (Resume JSON) & Adapter C (Structured Gen) & Question-Rubric Tables / Roadmaps \\
    \texttt{general\_response} & MongoDB (Session History) & Adapter B (HR Coach) & Conversational Vietnamese Dialogue \\
    \hline\hline
    \end{tabular}
\end{table}
```

#### 4.3 Dataset Statistics (Line 1037-1052)
**Before:**
```latex
\begin{table}[H]
    \centering
    \caption[Dataset Statistics]{\textbf{Dataset Statistics}}
    \vspace{0.2cm}
    \resizebox{\textwidth}{!}{
    \begin{tabular}{l|l|c|c|c|c}
    \hline\hline
    Dataset Target & Primary Purpose & SFT Train & SFT Val & DPO Pairs & Avg Token Length \\
    \hline
    \textbf{Adapter A} & Intent Classification & 4,869 & 542 & - & 355 \\
    \textbf{Adapter B} & Empathy \& Metric Coaching & 1,656 & 185 & 1,841 & 1,490 \\
    \textbf{Adapter C} & Markdown Tables \& Rubrics & 820 & 92 & - & 1,024 \\
    \hline\hline
    \end{tabular}
    }
\end{table}
```

**After:**
```latex
\begin{table}[H]
    \centering
    \caption[Dataset Statistics]{\textbf{Dataset Statistics}}
    \vspace{0.2cm}
    \large
    \renewcommand{\arraystretch}{1.3}
    \begin{tabular}{p{2.8cm} | p{4.2cm} | c | c | c | c}
    \hline\hline
    Dataset Target & Primary Purpose & SFT Train & SFT Val & DPO Pairs & Avg Token Length \\
    \hline
    \textbf{Adapter A} & Intent Classification & 4,869 & 542 & - & 355 \\
    \textbf{Adapter B} & Empathy \& Metric Coaching & 1,656 & 185 & 1,841 & 1,490 \\
    \textbf{Adapter C} & Markdown Tables \& Rubrics & 820 & 92 & - & 1,024 \\
    \hline\hline
    \end{tabular}
\end{table}
```

#### 4.4 Adapter Performance Benchmark (Line 1082-1098)
**Before:**
```latex
\begin{table}[H]
    \centering
    \caption[Adapter Performance Benchmark]{\textbf{Adapter Performance Benchmark}}
    \vspace{0.2cm}
    \resizebox{\textwidth}{!}{
    \begin{tabular}{l|l|c|c|c|c}
    \hline\hline
    Track & Target Component & Base Model Score & Fine-Tuned Adapter & Pass Threshold & Status \\
    \hline
    \textbf{1. Extraction} & Parsing Cascade & - & 97.3\% Schema Accuracy & $\ge 80.0\%$ Accuracy & PASS \\
    \textbf{2. HR Feedback} & Adapter B (DPO) & 1.2 / 10 & 7.8 / 10 & $\ge 7.0 / 10$ & PASS \\
    \textbf{3. Tool Calling} & Adapter A (Classifier) & 50.0\% & 98.0\% Accuracy & $\ge 90.0\%$ Accuracy & PASS \\
    \textbf{4. Structured Gen} & Adapter C (Structured) & 3.6 / 10 & 8.1 / 10 & $\ge 7.0 / 10$ & PASS \\
    \hline\hline
    \end{tabular}
    }
\end{table}
```

**After:**
```latex
\begin{table}[H]
    \centering
    \caption[Adapter Performance Benchmark]{\textbf{Adapter Performance Benchmark}}
    \vspace{0.2cm}
    \large
    \renewcommand{\arraystretch}{1.3}
    \begin{tabular}{p{2.5cm} | p{3.2cm} | c | c | c | c}
    \hline\hline
    Track & Target Component & Base Model Score & Fine-Tuned Adapter & Pass Threshold & Status \\
    \hline
    \textbf{1. Extraction} & Parsing Cascade & - & 97.3\% Schema Accuracy & $\ge 80.0\%$ Accuracy & PASS \\
    \textbf{2. HR Feedback} & Adapter B (DPO) & 1.2 / 10 & 7.8 / 10 & $\ge 7.0 / 10$ & PASS \\
    \textbf{3. Tool Calling} & Adapter A (Classifier) & 50.0\% & 98.0\% Accuracy & $\ge 90.0\%$ Accuracy & PASS \\
    \textbf{4. Structured Gen} & Adapter C (Structured) & 3.6 / 10 & 8.1 / 10 & $\ge 7.0 / 10$ & PASS \\
    \hline\hline
    \end{tabular}
\end{table}
```

#### 4.5 Summary of Aggregated Job Market Data (Line 1144-1162)
**Before:**
```latex
\begin{table}[H]
    \centering
    \caption[Summary of Aggregated Job Market Data]{\textbf{Summary of Aggregated Job Market Data}}
    \vspace{0.2cm}
    \resizebox{\textwidth}{!}{
    \begin{tabular}{l|l|l}
    \hline\hline
    Metric & Observed Value & Description \\
    \hline
    \textbf{Total Jobs Crawled} & 6,248 & Total rows extracted from JobOKO and TopCV \\
    \textbf{Unique Companies} & 1,482 & Distinct employers identified in listings \\
    \textbf{Normalisation Success Rate} & 85.3\% & Percentage of jobs passing rule-based validation verification \\
    \textbf{Standardised Categories} & 66 & Unified taxonomy tags for classification \\
    \textbf{Geographical Cities} & 4 & Hanoi, Ho Chi Minh City, Da Nang, and Binh Duong \\
    \textbf{Scraping Frequency} & Every 3 days & Automated GitHub Actions execution interval \\
    \hline\hline
    \end{tabular}
    }
\end{table}
```

**After:**
```latex
\begin{table}[H]
    \centering
    \caption[Summary of Aggregated Job Market Data]{\textbf{Summary of Aggregated Job Market Data}}
    \vspace{0.2cm}
    \large
    \renewcommand{\arraystretch}{1.3}
    \begin{tabular}{p{4cm} | p{2.5cm} | p{8cm}}
    \hline\hline
    Metric & Observed Value & Description \\
    \hline
    \textbf{Total Jobs Crawled} & 6,248 & Total rows extracted from JobOKO and TopCV \\
    \textbf{Unique Companies} & 1,482 & Distinct employers identified in listings \\
    \textbf{Normalisation Success Rate} & 85.3\% & Percentage of jobs passing rule-based validation verification \\
    \textbf{Standardised Categories} & 66 & Unified taxonomy tags for classification \\
    \textbf{Geographical Cities} & 4 & Hanoi, Ho Chi Minh City, Da Nang, and Binh Duong \\
    \textbf{Scraping Frequency} & Every 3 days & Automated GitHub Actions execution interval \\
    \hline\hline
    \end{tabular}
\end{table}
```

#### 4.6 Search Latency under Varying Concurrent Queries (Line 1173-1189)
**Before:**
```latex
\begin{table}[H]
    \centering
    \caption[Search Latency under Varying Concurrent Queries]{\textbf{Search Latency under Varying Concurrent Queries}}
    \vspace{0.2cm}
    \resizebox{\textwidth}{!}{
    \begin{tabular}{l|c|c|c}
    \hline\hline
    Concurrent Requests & 50th Percentile Latency (ms) & 90th Percentile Latency (ms) & 99th Percentile Latency (ms) \\
    \hline
    \textbf{1 (Single user)} & 12.4 ms & 28.1 ms & 45.2 ms \\
    \textbf{10 concurrent} & 18.5 ms & 37.4 ms & 62.1 ms \\
    \textbf{50 concurrent} & 32.1 ms & 64.8 ms & 112.5 ms \\
    \textbf{100 concurrent} & 58.4 ms & 114.2 ms & 198.6 ms \\
    \hline\hline
    \end{tabular}
    }
\end{table}
```

**After:**
```latex
\begin{table}[H]
    \centering
    \caption[Search Latency under Varying Concurrent Queries]{\textbf{Search Latency under Varying Concurrent Queries}}
    \vspace{0.2cm}
    \large
    \renewcommand{\arraystretch}{1.3}
    \begin{tabular}{p{4cm} | c | c | c}
    \hline\hline
    Concurrent Requests & 50th Percentile Latency (ms) & 90th Percentile Latency (ms) & 99th Percentile Latency (ms) \\
    \hline
    \textbf{1 (Single user)} & 12.4 ms & 28.1 ms & 45.2 ms \\
    \textbf{10 concurrent} & 18.5 ms & 37.4 ms & 62.1 ms \\
    \textbf{50 concurrent} & 32.1 ms & 64.8 ms & 112.5 ms \\
    \textbf{100 concurrent} & 58.4 ms & 114.2 ms & 198.6 ms \\
    \hline\hline
    \end{tabular}
\end{table}
```

#### 4.7 Comparative Performance of Base Model vs. Fine-Tuned Adapters (Line 1200-1216)
**Before:**
```latex
\begin{table}[H]
    \centering
    \caption[Comparative Performance of Base Model vs. Fine-Tuned Adapters]{\textbf{Comparative Performance of Base Model vs. Fine-Tuned Adapters}}
    \vspace{0.2cm}
    \resizebox{\textwidth}{!}{
    \begin{tabular}{l|l|c|c|c}
    \hline\hline
    Track / Adapter & Evaluation Objective & Base Model Score & Fine-Tuned Adapter & Status / Pass Threshold \\
    \hline
    \textbf{1. Extraction Cascade} & Schema alignment from raw CVs & 68.2\% & \textbf{97.3\%} & PASS ($\ge 80.0\%$) \\
    \textbf{2. Adapter A (Classifier)} & Intent / tool routing accuracy & 50.0\% & \textbf{98.0\%} & PASS ($\ge 90.0\%$) \\
    \textbf{3. Adapter B (HR Coach)} & Empathy \& Metric-based coaching & 1.2 / 10 & \textbf{7.8 / 10} & PASS ($\ge 7.0 / 10$) \\
    \textbf{4. Adapter C (Structured)} & Tabular formatting \& roadmap scoring & 3.6 / 10 & \textbf{8.1 / 10} & PASS ($\ge 7.0 / 10$) \\
    \hline\hline
    \end{tabular}
    }
\end{table}
```

**After:**
```latex
\begin{table}[H]
    \centering
    \caption[Comparative Performance of Base Model vs. Fine-Tuned Adapters]{\textbf{Comparative Performance of Base Model vs. Fine-Tuned Adapters}}
    \vspace{0.2cm}
    \large
    \renewcommand{\arraystretch}{1.3}
    \begin{tabular}{p{2.5cm} | p{3.2cm} | c | c | c}
    \hline\hline
    Track / Adapter & Evaluation Objective & Base Model Score & Fine-Tuned Adapter & Status / Pass Threshold \\
    \hline
    \textbf{1. Extraction Cascade} & Schema alignment from raw CVs & 68.2\% & \textbf{97.3\%} & PASS ($\ge 80.0\%$) \\
    \textbf{2. Adapter A (Classifier)} & Intent / tool routing accuracy & 50.0\% & \textbf{98.0\%} & PASS ($\ge 90.0\%$) \\
    \textbf{3. Adapter B (HR Coach)} & Empathy \& Metric-based coaching & 1.2 / 10 & \textbf{7.8 / 10} & PASS ($\ge 7.0 / 10$) \\
    \textbf{4. Adapter C (Structured)} & Tabular formatting \& roadmap scoring & 3.6 / 10 & \textbf{8.1 / 10} & PASS ($\ge 7.0 / 10$) \\
    \hline\hline
    \end{tabular}
\end{table}
```

#### 4.8 Key Platform System Latency Metrics (Line 1227-1244)
*Note: This also fixes Mismatch 2, Occurrence 2.5.*

**Before:**
```latex
\begin{table}[H]
    \centering
    \caption[Key Platform System Latency Metrics]{\textbf{Key Platform System Latency Metrics}}
    \vspace{0.2cm}
    \resizebox{\textwidth}{!}{
    \begin{tabular}{l|l|l|l}
    \hline\hline
    System Workflow & Component Stack & Average Execution Time & Description \\
    \hline
    \textbf{Page Load Time (SSR)} & Next.js 16 [\hyperlink{cite1}{1}] + Supabase Auth & 1.45 seconds & Time to load index page with session cookies \\
    \textbf{Chatbot Response (Sync)} & FastAPI + Ollama Inference & 2.10 seconds & Time for Adapter A routing + Adapter B generation \\
    \textbf{CV Upload Ingestion (Async)} & Next.js BFF $\rightarrow$ FastAPI $\rightarrow$ GridFS & 0.85 seconds & Time to save file and return background Job ID \\
    \textbf{CV Background Processing} & Celery + PhoBERT [\hyperlink{cite8}{8}] + Qdrant & 34.20 seconds & Full extraction, NER, scoring, embedding, and storage \\
    \textbf{Scrape \& Normalise (300 jobs)} & Playwright + Heuristic Parser & 35.50 minutes & Ingestion of 300 jobs, including 10s anti-bot delay \\
    \hline\hline
    \end{tabular}
    }
\end{table}
```

**After:**
```latex
\begin{table}[H]
    \centering
    \caption[Key Platform System Latency Metrics]{\textbf{Key Platform System Latency Metrics}}
    \vspace{0.2cm}
    \large
    \renewcommand{\arraystretch}{1.3}
    \begin{tabular}{p{3.5cm} | p{3.5cm} | p{3cm} | p{5cm}}
    \hline\hline
    System Workflow & Component Stack & Average Execution Time & Description \\
    \hline
    \textbf{Page Load Time (SSR)} & Next.js 16 [\hyperlink{cite1}{1}] + Supabase Auth & 1.45 seconds & Time to load index page with session cookies \\
    \textbf{Chatbot Response (Sync)} & FastAPI + Ollama Inference & 2.10 seconds & Time for Adapter A routing + Adapter B generation \\
    \textbf{CV Upload Ingestion (Async)} & Next.js BFF $\rightarrow$ FastAPI $\rightarrow$ GridFS & 0.85 seconds & Time to save file and return background Job ID \\
    \textbf{CV Background Processing} & Celery + Electra NER [\hyperlink{cite8}{8}] + Qdrant & 34.20 seconds & Full extraction, NER, scoring, embedding, and storage \\
    \textbf{Scrape \& Normalise (300 jobs)} & Playwright + Heuristic Parser & 35.50 minutes & Ingestion of 300 jobs, including 10s anti-bot delay \\
    \hline\hline
    \end{tabular}
\end{table}
```

#### 4.9 Feature Comparison with Existing Platforms (Line 1285-1303)
**Before:**
```latex
\begin{table}[H]
    \centering
    \caption[Feature Comparison with Existing Platforms]{\textbf{Feature Comparison with Existing Platforms}}
    \vspace{0.2cm}
    \resizebox{\textwidth}{!}{
    \begin{tabular}{l|c|c|c|c}
    \hline\hline
    Architectural Feature & Our Platform & TopCV & LinkedIn & Glassdoor \\
    \hline
    \textbf{Vietnamese Job Focus} & \textbf{YES} & YES & PARTIAL & NO \\
    \textbf{Unified Analytics Dashboard} & \textbf{YES} & NO & PARTIAL & YES \\
    \textbf{Local AI Career Chatbot (SLM)} & \textbf{YES} & NO & NO & NO \\
    \textbf{CV Key Information Extraction} & \textbf{YES} & PARTIAL & YES & NO \\
    \textbf{Open Source / Self-Hosted} & \textbf{YES} & NO & NO & NO \\
    \textbf{Aspect-Specific Vector Match} & \textbf{YES} & NO & PARTIAL & NO \\
    \hline\hline
    \end{tabular}
    }
\end{table}
```

**After:**
```latex
\begin{table}[H]
    \centering
    \caption[Feature Comparison with Existing Platforms]{\textbf{Feature Comparison with Existing Platforms}}
    \vspace{0.2cm}
    \large
    \renewcommand{\arraystretch}{1.3}
    \begin{tabular}{p{5.5cm} | c | c | c | c}
    \hline\hline
    Architectural Feature & Our Platform & TopCV & LinkedIn & Glassdoor \\
    \hline
    \textbf{Vietnamese Job Focus} & \textbf{YES} & YES & PARTIAL & NO \\
    \textbf{Unified Analytics Dashboard} & \textbf{YES} & NO & PARTIAL & YES \\
    \textbf{Local AI Career Chatbot (SLM)} & \textbf{YES} & NO & NO & NO \\
    \textbf{CV Key Information Extraction} & \textbf{YES} & PARTIAL & YES & NO \\
    \textbf{Open Source / Self-Hosted} & \textbf{YES} & NO & NO & NO \\
    \textbf{Aspect-Specific Vector Match} & \textbf{YES} & NO & PARTIAL & NO \\
    \hline\hline
    \end{tabular}
\end{table}
```

---

## Verification Build

Once changes are applied, run this command to build the document and ensure zero errors:
```bash
.\thesis_2_latex\tectonic.exe thesis_1.tex
```
