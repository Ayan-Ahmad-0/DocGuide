import sys
sys.stdout.reconfigure(encoding="utf-8")
import json
from collections import Counter
from config import DOCUMENTS

docs = [json.loads(l) for l in DOCUMENTS.open(encoding="utf-8")]
counts = Counter(d["type"] for d in docs)
words = sum(len(d["text"].split()) for d in docs)

print("Counts:", dict(counts))
print(f"Total words: {words:,}")

problems = []
if counts["article"] != 99:
    problems.append(f"expected 99 articles, got {counts['article']}")
if counts["recital"] != 173:
    problems.append(f"expected 173 recitals, got {counts['recital']}")

for d in docs:
    if len(d["text"].split()) < 5:
        problems.append(f"{d['id']}: text too short")
    if d["type"] == "article" and not d["title"]:
        problems.append(f"{d['id']}: missing title")

# gaps in numbering
for t, n in (("article", 99), ("recital", 173)):
    have = {d["number"] for d in docs if d["type"] == t}
    missing = sorted(set(range(1, n + 1)) - have)
    if missing:
        problems.append(f"missing {t}s: {missing}")

# eyeball samples
for id_ in ("article-5", "recital-39"):
    d = next((x for x in docs if x["id"] == id_), None)
    if d:
        print(f"\n--- {id_} | {d['title']} ---\n{d['text'][:500]}")

print("\nPROBLEMS:" if problems else "\nALL CHECKS PASSED")
for p in problems:
    print(" -", p)