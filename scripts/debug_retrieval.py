# scripts/debug_retrieval.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import TOP_K
from src.embed import embed_query
from src.index import search


def debug_retrieve(question: str, fetch_n: int = 40):
    rows = search(embed_query(question), fetch_n)
    print(f"\nQuery: {question!r}")
    print(f"Top {len(rows)} raw candidates (before max_per_doc capping):\n")
    for i, r in enumerate(rows, 1):
        flag = " <-- article-83" if r["doc_id"] == "article-83" else ""
        print(f"{i:2d}. [{r['score']:.3f}] {r['citation']:20s} ({r['doc_id']}){flag}")

    print(f"\nWould survive into top-{TOP_K} after max_per_doc capping: "
          f"see which of the above make it — count per doc_id below.")
    from collections import Counter
    per_doc_order = Counter()
    for r in rows[:fetch_n]:
        per_doc_order[r["doc_id"]] += 1


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else \
        "Can a company be fined for failing to appoint a data protection officer when one is required?"
    debug_retrieve(q)