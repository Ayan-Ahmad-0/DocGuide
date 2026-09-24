from config import TOP_K
from src.embed import embed_query
from src.index import search


def retrieve(question: str, k: int = TOP_K) -> list[dict]:
    rows = search(embed_query(question), k)
    return [
        {
            "citation": r["citation"],
            "doc_id": r["doc_id"],
            "title": r["title"],
            "score": round(float(r["score"]), 3),
            "text": r["text"],
        }
        for r in rows
    ]