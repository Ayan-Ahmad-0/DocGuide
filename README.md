# DocGuide GDPR(General Data Protection Regulation) Research Assistant

A Retrieval-Augmented Generation assistant that answers questions about the GDPR using only the official text — every claim is cited, every citation is checked against what was actually retrieved, and the assistant says so when the regulation doesn't cover something.

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Neon](https://img.shields.io/badge/Neon-00E599?style=flat&logo=neon&logoColor=white)](https://neon.tech/)
[![pgvector](https://img.shields.io/badge/pgvector-4169E1?style=flat)](https://github.com/pgvector/pgvector)
[![Gemini](https://img.shields.io/badge/Gemini-8E75B2?style=flat&logo=googlegemini&logoColor=white)](https://ai.google.dev/)

---

## 📋 Overview

DocGuide is a grounded question-answering assistant over the full text of the GDPR (articles and recitals, fetched from EUR-Lex). It:

1. **Fetches and parses** the official GDPR text from EUR-Lex into structured articles and recitals
2. **Chunks** the text by paragraph/sub-clause, keeping citations precise down to the sub-paragraph level (e.g. `Article 83(4)`, not just `Article 83`)
3. **Embeds** each chunk locally (`BAAI/bge-small-en-v1.5`) and indexes it in **Postgres + pgvector**, hosted on **Neon**
4. **Retrieves** the most relevant passages for a question, diversified across articles so no single clause dominates the context
5. **Generates** a cited answer with a Gemini model, instructed to answer only from retrieved passages and explicitly refuse when the GDPR doesn't cover something
6. **Verifies** every citation the model produces against what was actually retrieved — invented citations are flagged, not hidden
7. Is **measured**, not just demoed: a 47-question evaluation set scores correctness, refusal accuracy, cost, and latency on every change to the pipeline
8. Is served through a **Streamlit assistant UI**, deployed publicly on **Streamlit Community Cloud**

This mirrors how a production RAG system is actually validated for a specialized document — not just "does it sound right," but "is every claim traceable to the source, and how often does it get that wrong."

---

## 🏗️ Architecture

**EUR-Lex (GDPR HTML)** → **Parse & Chunk (Python)** → **Local Embeddings (bge-small-en-v1.5)** → **Postgres + pgvector (Neon)** → **Retrieve + Generate (Gemini)** → **Streamlit Assistant (Streamlit Community Cloud)**

| Stage | Purpose | Format | Storage |
|---|---|---|---|
| **Fetch** | Pull the GDPR HTML from EUR-Lex | HTML | `data/raw/gdpr.html` |
| **Parse** | Split into articles + recitals | JSON lines | `data/processed/documents.jsonl` |
| **Chunk** | Paragraph-level chunks, ≤280 words, with citation labels | JSON lines | `data/processed/chunks.jsonl` |
| **Embed + Index** | Local embeddings, stored as vectors | 384-dim vectors | Postgres + pgvector (Neon) |
| **Retrieve** | Top-K similarity search, capped per document | Ranked chunks | In-memory per request |
| **Answer** | Cited response from retrieved chunks only | Markdown + citations | Returned to the UI |
| **Serve** | Chat interface with sources and verification | — | Streamlit (Streamlit Community Cloud) |

### Architecture Diagram

<!-- Add: images/architecture_diagram.png -->
![Architecture Diagram](images/architecture_diagram.png)

### Tech Stack

- **Fetching & parsing:** Python, EUR-Lex HTML as the single corpus source — parsed into 99 articles and 173 recitals (~52,900 words)
- **Chunking:** Paragraph-aware splitter that respects article sub-clause boundaries, merges undersized fragments, and splits oversized ones at sentence boundaries — ~444 chunks total
- **Embeddings:** Local `BAAI/bge-small-en-v1.5` (384 dimensions) via `sentence-transformers` — no external quota limits, no embedding cost
- **Vector store:** Postgres with the `pgvector` extension, hosted on **Neon** (serverless Postgres, free tier)
- **Retrieval:** Over-fetch + diversify — pulls `TOP_K * 4` candidates, then caps how many chunks can come from a single article/recital so sources stay varied rather than dominated by one clause
- **Generation:** Gemini (`gemini-3.1-flash-lite`), temperature 0, strict system prompt: answer only from retrieved passages, cite every claim, refuse explicitly when the passages don't cover the question
- **Citation verification:** Every citation the model outputs is checked against the citations actually present in the retrieved chunks — unsupported citations are surfaced, not silently trusted
- **Evaluation:** A 47-question set spanning answerable, out-of-scope, and genuinely ambiguous ("partial") questions, graded automatically for correctness, faithfulness, refusal accuracy, cost, and latency
- **Frontend:** Streamlit — chat interface, expandable source cards with similarity scores, per-response cost/latency/token badges, deployed on **Streamlit Community Cloud**

---

## 📊 Assistant Output

<!-- Add: images/app_chat.png, images/app_sources.png -->
![Chat View](images/app_chat.png)
![Sources & Citation Verification](images/app_sources.png)

---

## 🔄 Pipeline Flow

```
Fetch GDPR HTML (EUR-Lex)
        │
        ▼
Parse into articles + recitals (documents.jsonl)
        │
        ▼
Chunk by paragraph, ≤280 words, citation-labeled (chunks.jsonl)
        │
        ▼
Embed locally (bge-small-en-v1.5) → Index in Postgres + pgvector (Neon)
        │
        ▼
Retrieve (over-fetch → diversify by document) → top-K chunks
        │
        ▼
Generate cited answer (Gemini) → verify citations against retrieved chunks
        │
        ▼
Streamlit Assistant on Streamlit Community Cloud
```

Each stage writes its own intermediate file (`documents.jsonl`, `chunks.jsonl`), so any stage can be re-run in isolation — re-chunking doesn't require re-fetching, re-embedding doesn't require re-chunking unless the chunks actually changed.

---

## ✅ Evaluation Results

A 47-question set — 37 answerable, 8 deliberately out-of-scope, 2 genuinely ambiguous under the GDPR itself — run automatically end-to-end against the live retrieval + generation pipeline:

| Metric | Result |
|---|---|
| Judged correct | 35 / 37 |
| Judged partial | 2 / 37 |
| Judged incorrect | 0 |
| Judged error | 0 |
| Correct refusals (out-of-scope) | 8 / 8 |
| Correct refusals (ambiguous) | 2 / 2 |
| False refusals (answerable, wrongly refused) | 0 |
| Average cost per question | ~$0.0006 |
| Average latency per question | ~6s |

<!-- Add: images/eval_report.png -->
![Evaluation Report](images/eval_report.png)

The one false refusal found during development (a question about DPO-related fines under Article 83(4)) traced to a retrieval gap, not a model or prompt issue — Article 83(4)'s text is a dense list of cross-referenced article numbers with no descriptive language, so it embedded poorly against natural-language questions. Fixed by enriching that chunk's embedding text with a short topic gloss, without altering the actual cited text shown to users. See **Challenges Solved** below.

---

## 🗂️ Vector Store (Postgres + pgvector on Neon)

| Object | Description |
|---|---|
| Chunks table | One row per chunk — citation label, article/recital number, chunk text, 384-dim embedding vector |
| Similarity search | Cosine similarity via `pgvector`, queried per request through a pooled connection |

---

## 🔒 Grounding & Reliability

- **Strict grounding** — the system prompt instructs the model to answer only from retrieved passages, never from general knowledge of the GDPR
- **Explicit refusal** — a fixed refusal token/message is used when retrieved passages don't cover the question, rather than letting the model improvise an answer it can't support
- **Citation verification** — every citation in a generated answer is checked against the citations actually present in the retrieved chunks; unsupported citations are flagged in the UI, not hidden
- **Diversified retrieval** — a per-document cap on retrieved chunks keeps one heavily-matching article/recital from crowding out everything else in the context
- **Reference glosses for cross-reference-heavy clauses** — chunks that are mostly lists of article numbers (e.g. penalty clauses referencing "Articles 25 to 39") get a short topic gloss appended to their *embedding* text only, so they surface for natural-language questions without altering the actual legal text shown to users
- **Resumable, cost-aware evaluation** — the eval script skips already-graded questions on rerun, so a partial run or a targeted re-test doesn't re-pay for the whole 47-question set

---

## 📁 Repository Structure

```
docguide/
├── README.md
├── requirements.txt
├── .env.example
├── config.py                      # All paths, model names, retrieval/chunking constants
├── app.py                         # Streamlit assistant UI
│
├── .streamlit/
│   └── config.toml                # Theme (committed — no secrets here)
│
├── data/
│   ├── raw/
│   │   └── gdpr.html              # Fetched EUR-Lex source
│   └── processed/
│       ├── documents.jsonl        # Parsed articles + recitals
│       └── chunks.jsonl           # Paragraph-level chunks with citations
│
├── src/
│   ├── chunk.py                   # Paragraph-aware chunking + reference glosses
│   ├── embed.py                   # Local embedding model client
│   ├── index.py                   # pgvector search
│   ├── retrieve.py                # Over-fetch + per-document diversification
│   ├── prompts.py                 # System prompt, refusal token/message
│   ├── citations.py               # Citation extraction + unsupported-citation check
│   ├── cost.py                    # Per-question cost estimation
│   └── answer.py                  # End-to-end ask(question) -> result dict
│
├── scripts/
│   ├── build_index.py             # Fetch → parse → chunk → embed → index, resumable
│   ├── smoke_test.py              # Quick 7-question retrieval sanity check
│   └── debug_retrieval.py         # Raw ranked-candidate inspector for a query
│
├── eval/
│   ├── run_eval.py                # Resumable, append-only evaluation run
│   ├── metrics.py                 # Builds the markdown report from raw results
│   └── results/
│       └── baseline.jsonl         # Raw per-question graded results
│
└── data/eval/
    └── questions.jsonl            # 47-question evaluation set
```

---

## ⚙️ Configuration

Create a `.env` file in the project root (used locally, and mirrored in Streamlit Secrets when deployed):

```
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://user:password@your-neon-host-pooler.neon.tech/dbname?sslmode=require
```

- `DATABASE_URL` should use Neon's **pooled connection string** (hostname contains `-pooler`), with `?sslmode=require` — Neon rejects unencrypted connections
- On **Streamlit Community Cloud**, the same two keys are added under **Settings → Secrets** in TOML format; never committed to the repo
- `sentence-transformers`/`torch` are installed CPU-only in `requirements.txt` (`--extra-index-url https://download.pytorch.org/whl/cpu`) to keep the deployed build small — the local embedding model doesn't need GPU support

---

## 🚀 Getting Started

```
# Clone the repo
git clone https://github.com/Ayan-Ahmad-0/docguide.git
cd docguide

# Create a .env file with your Gemini API key and Neon connection string (see Configuration above)

# Install dependencies
pip install -r requirements.txt

# Build the corpus: fetch, parse, chunk, embed, index (resumable — safe to re-run)
python scripts/build_index.py

# Sanity-check retrieval quality
python scripts/smoke_test.py

# Run the full evaluation set
python -m eval.run_eval
python -m eval.metrics

# Run the assistant locally
streamlit run app.py
```

| Service | URL |
|---|---|
| Assistant (local) | <http://localhost:8501> |
| Assistant (live) | Deployed on Streamlit Community Cloud |
| Vector store | Neon (managed Postgres + pgvector, not local) |

---

## 🚧 Challenges Solved

- Hit Gemini embedding **quota limits (429 errors)** mid-build; switched from `gemini-embedding-001` (768-dim) to a local `bge-small-en-v1.5` model (384-dim) — removes quota risk entirely and drops embedding cost to zero, at a small retrieval-quality tradeoff (Hit@5 6/7 vs. 7/7 in the smoke test)
- Diagnosed a **false refusal** on an answerable question (DPO-related fines under Article 83(4)) by tracing it through raw ranked retrieval output — the correct clause scored *lower* than five sibling sub-clauses of the same article because its text is a dense cross-reference list with no descriptive language
- Fixed the retrieval gap by appending a short topic gloss to that chunk's **embedding text only** (never the text shown to users), pulling Article 83(4) from rank 24 to rank 2 for the failing query without touching any other chunk's ranking
- Traced several `ModuleNotFoundError` issues to Python's `sys.path` only including the entry script's own directory, not the project root — fixed by running pipeline scripts as modules (`python -m eval.run_eval`) or via an explicit path fix, and by moving `app.py` to the repo root so Streamlit Cloud's deployment path resolves `src/` correctly
- Diagnosed a re-run of the evaluation script returning **identical results** to a prior run — the script is intentionally resumable/append-only and was skipping every already-graded question by ID; fixed by rotating out the old results file before a deliberate full re-run
- Fixed an invalid `requirements.txt` line (`package --index-url url` isn't valid pip-requirements syntax) that was silently breaking the deployed build; moved the CPU-only PyTorch index to its own `--extra-index-url` line
- Fixed a Streamlit theming issue where custom CSS set a light background while native widgets inherited a dark-mode text color from the browser/OS, making text invisible — resolved via an explicit `.streamlit/config.toml` theme, which reliably overrides OS/browser theme preference for every native widget

---

## 🛠️ Future Improvements

- Test loosening the refusal rule on genuinely ambiguous/partial questions to see whether a hedged partial answer serves users better than a flat refusal, without hurting out-of-scope accuracy
- Add a lightweight reranking or hybrid BM25 + embedding retrieval step to close the remaining gap on other cross-reference-heavy clauses beyond the one found so far
- Record a short demo walkthrough of the deployed assistant