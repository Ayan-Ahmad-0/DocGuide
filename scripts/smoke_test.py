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

hits = 0
for q, expected in TESTS:
    results = retrieve(q, k=5)
    found = any(r["doc_id"] in expected for r in results)
    hits += found
    print(f"\n{'HIT ' if found else 'MISS'} | {q}")
    for r in results:
        print(f"   {r['score']:.3f}  {r['citation']}  {r['title'] or ''}")

print(f"\nTop-5 hit rate: {hits}/{len(TESTS)}")