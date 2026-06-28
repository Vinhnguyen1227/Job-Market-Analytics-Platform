# Plan: Create Agent Guide for Thesis Mismatches

Me plan to write guide file for another agent to fix factual mismatches in `thesis_1.tex`.

## User Review Required

> [!IMPORTANT]
> Guide will tell agent to change `thesis_1.tex` text. Me not change `thesis_1.tex` directly. Guide will list exact replacements.

## Proposed Changes

### Documentation Components

#### [NEW] [thesis_mismatches_fix_guide.md](file:///d:/Job-Market-Analytics-Platform/thesis_mismatches_fix_guide.md)
* Guide file containing instructions for editing `thesis_1.tex` to fix mismatches.
* List five sections to edit:
  1. **Section 1.2.2 (Full-Text Search and Vector Retrieval)**: Change text to clarify that only resumes are encoded as vectors in Qdrant, while job descriptions are indexed in Elasticsearch (full-text search) and matched via keyword/token overlap, not job description vector indexing.
  2. **Chapter 1, 3, 4, 5 (PhoBERT NER)**: Change "PhoBERT" to "Electra-based model" (specifically `NlpHUST/ner-vietnamese-electra-base`) where NER is mentioned, including references.
  3. **Section 4.2 (Elasticsearch Search Performance)**: Remove claim that job descriptions are boosted/searched in Elasticsearch index. Only title and company are searched and boosted.
  4. **Section 4.4 (End-to-End System Latency Metrics)**: In Table 4 (CV Background Processing), change "Celery + PhoBERT" to "Celery + Electra NER" to match the actual model used.
  5. **Section 4.1 (Geographical Cities)**: Clarify that system supports 64+ cities, but offline normalization script maps Hanoi, Ho Chi Minh, and Da Nang with aliases.

## Verification Plan

### Manual Verification
* User check guide content.
* Once approved, user run next agent on guide to update `thesis_1.tex`.
