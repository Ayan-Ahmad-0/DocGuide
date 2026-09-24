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
TOP_K = 5

# ---------- Embeddings (Gemini) ----------
EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 768   # must match the vector(768) column in Postgres

# ---------- Database (Postgres + pgvector, e.g. Neon) ----------
DATABASE_URL = os.getenv("DATABASE_URL")