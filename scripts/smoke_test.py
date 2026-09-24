import sys
from src.retrieve import retrieve

sys.stdout.reconfigure(encoding="utf-8")

# (question, acceptable doc_ids)
TESTS = [
    ("How long can personal data be stored?", {"article-5", "recital-39"}),
    ("What is the right to erasure?", {"article-17"}),
    ("When must a data breach be reported to the authority?", {"article-33"}),
    ("What are the maximum fines for infringements?", {"article-83"}),
    ("How does the GDPR define personal data?", {"article-4"}),
    ("When is a data protection officer required?", {"article-37"}),
    ("What are the conditions for valid consent?", {"article-7", "article-4"}),
]

hit5 = hit8 = 0
for q, expected in TESTS:
    results = retrieve(q, k=10)
    rank = next((i + 1 for i, r in enumerate(results) if r["doc_id"] in expected), None)
    hit5 += bool(rank and rank <= 5)
    hit8 += bool(rank and rank <= 8)
    print(f"\n{'HIT ' if rank and rank <= 8 else 'MISS'} | first correct rank: {rank} | {q}")
    for i, r in enumerate(results[:8], 1):
        mark = "*" if r["doc_id"] in expected else " "
        print(f" {mark} {i:>2}. {r['score']:.3f}  {r['citation']}  {r['title'] or ''}")

print(f"\nHit@5: {hit5}/{len(TESTS)}   Hit@8: {hit8}/{len(TESTS)}")