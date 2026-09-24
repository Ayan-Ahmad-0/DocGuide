import hashlib
import json
import sys
import time
from config import CHUNKS, PROCESSED_DIR
from src.embed import embed_texts, PAUSE
from src.index import add_chunks

sys.stdout.reconfigure(encoding="utf-8")

CACHE = PROCESSED_DIR / "embeddings_cache.jsonl"
PART = 64   # save progress after every 64 chunks


def key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


chunks = [json.loads(l) for l in CHUNKS.open(encoding="utf-8")]

cache = {}
if CACHE.exists():
    for line in CACHE.open(encoding="utf-8"):
        row = json.loads(line)
        cache[row["key"]] = row["vec"]

todo = [c for c in chunks if key(c["embed_text"]) not in cache]
print(f"{len(chunks)} chunks: {len(chunks) - len(todo)} cached, {len(todo)} to embed")

with CACHE.open("a", encoding="utf-8") as f:
    for i in range(0, len(todo), PART):
        part = todo[i:i + PART]
        vecs = embed_texts([c["embed_text"] for c in part])
        for c, v in zip(part, vecs):
            k = key(c["embed_text"])
            cache[k] = v
            f.write(json.dumps({"key": k, "vec": v}) + "\n")
        f.flush()
        if PAUSE and i + PART < len(todo):
            time.sleep(PAUSE)

embeddings = [cache[key(c["embed_text"])] for c in chunks]
print("Indexed", add_chunks(chunks, embeddings), "chunks into Postgres")