from pathlib import Path

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

RAW_HTML = RAW_DIR / "gdpr.html"
DOCUMENTS = PROCESSED_DIR / "documents.jsonl"

# The ONLY corpus-specific setting. Swap if the partners pick another corpus.
SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679"