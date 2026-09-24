from functools import lru_cache
from google import genai
from sentence_transformers import SentenceTransformer
from config import EMBED_MODEL, QUERY_PREFIX

PAUSE = 0
_client = None


def _get_client():   # still used by src/answer.py for the Gemini answer step
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


@lru_cache(maxsize=1)
def _model():
    return SentenceTransformer(EMBED_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    return _model().encode(
        texts, batch_size=32, normalize_embeddings=True, show_progress_bar=True
    ).tolist()


def embed_query(question: str) -> list[float]:
    return _model().encode(QUERY_PREFIX + question, normalize_embeddings=True).tolist()