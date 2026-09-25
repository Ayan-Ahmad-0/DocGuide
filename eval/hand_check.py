import argparse
import json
import random
import sys
from config import EVAL_RESULTS_DIR

sys.stdout.reconfigure(encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("--name", default="baseline")
ap.add_argument("--n", type=int, default=10)
args = ap.parse_args()

rows = [json.loads(l) for l in (EVAL_RESULTS_DIR / f"{args.name}.jsonl").open(encoding="utf-8")]
graded = [r for r in rows if r.get("judge", {}).get("correctness") in ("correct", "partial", "incorrect")]
random.Random(7).shuffle(graded)
sample = graded[: args.n]

agree = 0
for i, r in enumerate(sample, 1):
    print("=" * 72)
    print(f"{i}/{len(sample)}  {r['question']}")
    print("\nREFERENCE:", r["reference"])
    print("\nANSWER:", r["answer"])
    j = r["judge"]
    print(f"\nJUDGE SAYS: {j['correctness']} | faithful: {j['faithful']} | {j['reason']}")
    agree += input("Do you agree with the correctness verdict? [y/n] ").strip().lower() == "y"

print(f"\nYou agreed with the judge on {agree}/{len(sample)} answers.")