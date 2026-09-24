import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")   # reads GEMINI_API_KEY and DATABASE_URL

# ---------- Paths ----------
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

RAW_HTML = RAW_DIR / "gdpr.html"
DOCUMENTS = PROCESSED_DIR / "documents.jsonl"
CHUNKS = PROCESSED_DIR / "chunks.jsonl"

# ---------- Corpus ----------
# The ONLY corpus-specific setting. Swap if the partners pick another corpus.
SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679"

# ---------- Chunking ----------
MAX_WORDS = 280   # a chunk never exceeds this
MIN_WORDS = 60    # smaller pieces get merged with a neighbour

# ---------- Retrieval ----------
TOP_K = 8          # passages sent to the LLM
MAX_PER_DOC = 3    # at most this many chunks from one article/recital (keeps sources varied)

# ---------- Embeddings (Gemini) ----------
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_DIM = 384   # must match the vector(768) column in Postgres

# ---------- LLM (Gemini) ----------
LLM_MODEL = "gemini-3.1-flash-lite"   # copy the exact ID from AI Studio if you get a 404
MAX_OUTPUT_TOKENS = 2048              # generous: "thinking" tokens count against this

# USD per 1M tokens (standard paid tier). Check Google's pricing page and put the date in your README.
LLM_PRICE_IN = 0.25
LLM_PRICE_OUT = 1.50
EMBED_PRICE_IN = 0.00   # gemini-embedding-001
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
# ---------- Database (Postgres + pgvector, e.g. Neon) ----------
DATABASE_URL = os.getenv("DATABASE_URL")