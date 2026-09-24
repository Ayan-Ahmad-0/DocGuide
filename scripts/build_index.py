import json
import sys
from config import CHUNKS
from src.embed import embed_texts
from src.index import add_chunks

sys.stdout.reconfigure(encoding="utf-8")

chunks = [json.loads(l) for l in CHUNKS.open(encoding="utf-8")]
print(f"Embedding {len(chunks)} chunks (first run downloads the model)...")
embeddings = embed_texts([c["embed_text"] for c in chunks])
count = add_chunks(chunks, embeddings)
print(f"Indexed {count} chunks into pg-vector db")