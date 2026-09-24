import math
import time
from google import genai
from google.genai import types
from config import EMBED_MODEL, EMBED_DIM

BATCH = 16
PAUSE = 10   # seconds between batches, to stay under free-tier limits. Set 0 on a paid key.

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client()   # reads GEMINI_API_KEY from the environment
    return _client


def _normalize(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]      # smaller-than-default sizes need normalizing for cosine search


def _embed(texts, task_type):
    for attempt in range(6):
        try:
            res = _get_client().models.embed_content(
                model=EMBED_MODEL,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type=task_type, output_dimensionality=EMBED_DIM
                ),
            )
            return [_normalize(e.values) for e in res.embeddings]
        except Exception as e:
            wait = 20 * (attempt + 1)
            print(f"  embed error ({e.__class__.__name__}), retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError("Embedding failed after 6 attempts")


def embed_texts(texts: list[str]) -> list[list[float]]:
    out = []
    for i in range(0, len(texts), BATCH):
        out += _embed(texts[i:i + BATCH], "RETRIEVAL_DOCUMENT")
        print(f"  embedded {min(i + BATCH, len(texts))}/{len(texts)}")
        if PAUSE and i + BATCH < len(texts):
            time.sleep(PAUSE)
    return out


def embed_query(question: str) -> list[float]:
    return _embed([question], "RETRIEVAL_QUERY")[0]