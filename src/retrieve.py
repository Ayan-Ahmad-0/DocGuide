from config import TOP_K, MAX_PER_DOC
from src.embed import embed_query
from src.index import search


def retrieve(question: str, k: int = TOP_K, max_per_doc: int = MAX_PER_DOC) -> list[dict]:
    rows = search(embed_query(question), k * 4)   # over-fetch, then diversify
    picked, per_doc = [], {}
    for r in rows:
        if per_doc.get(r["doc_id"], 0) >= max_per_doc:
            continue
        per_doc[r["doc_id"]] = per_doc.get(r["doc_id"], 0) + 1
        picked.append({
            "citation": r["citation"],
            "doc_id": r["doc_id"],
            "title": r["title"],
            "score": round(float(r["score"]), 3),
            "text": r["text"],
        })
        if len(picked) == k:
            break
    return picked