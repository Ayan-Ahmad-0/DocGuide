import argparse
import json
import sys
import time
from google.genai import errors, types
from config import EVAL_QUESTIONS, EVAL_RESULTS_DIR, JUDGE_MODEL, EVAL_PAUSE
from src.answer import ask
from src.embed import _get_client
from eval.metrics import build_report

sys.stdout.reconfigure(encoding="utf-8")

JUDGE_PROMPT = """You are grading an answer from a GDPR question-answering assistant.

QUESTION: {question}

REFERENCE FACTS (the answer should agree with these): {reference}

RETRIEVED PASSAGES (the only text the assistant was allowed to use):
{passages}

ASSISTANT ANSWER:
{answer}

Return JSON with exactly these keys:
- "correctness": "correct" if the answer states the key reference facts without contradicting them (extra accurate detail is fine); "partial" if it is missing important facts or is vague; "incorrect" if it contradicts the reference facts or misses the point.
- "faithful": true if every factual claim in the answer is supported by the retrieved passages, false if any claim is not.
- "reason": one short sentence."""


def judge(q: dict, result: dict) -> dict:
    passages = "\n\n".join(f"[{s['citation']}] {s['text']}" for s in result["sources"])
    prompt = JUDGE_PROMPT.format(
        question=q["question"], reference=q["reference"],
        passages=passages, answer=result["answer"],
    )
    for attempt in range(5):
        try:
            resp = _get_client().models.generate_content(
                model=JUDGE_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=1024,
                    response_mime_type="application/json",
                ),
            )
            break
        except errors.APIError as e:
            if e.code not in (429, 500, 503) or attempt == 4:
                raise
            time.sleep(15 * (attempt + 1))
    try:
        data = json.loads(resp.text)
        assert data["correctness"] in ("correct", "partial", "incorrect")
        data["faithful"] = bool(data.get("faithful"))
        return data
    except Exception:
        return {"correctness": "error", "faithful": False, "reason": "judge returned unusable output"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="baseline", help="label for this run")
    ap.add_argument("--limit", type=int, default=None, help="only run the first N questions")
    args = ap.parse_args()

    EVAL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = EVAL_RESULTS_DIR / f"{args.name}.jsonl"

    done = {}
    if out_path.exists():
        for line in out_path.open(encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                done[r["id"]] = r

    questions = [json.loads(l) for l in EVAL_QUESTIONS.open(encoding="utf-8") if l.strip()]
    questions = questions[: args.limit]

    with out_path.open("a", encoding="utf-8") as f:
        for i, q in enumerate(questions, 1):
            if q["id"] in done:
                continue
            print(f"[{i}/{len(questions)}] {q['id']}: {q['question']}")
            res = ask(q["question"])
            row = {
                **q,
                "answer": res["answer"],
                "refused": res["refused"],
                "citations": res["citations"],
                "unsupported_citations": res["unsupported_citations"],
                "uncited": res["uncited"],
                "sources": [{"citation": s["citation"], "doc_id": s["doc_id"]} for s in res["sources"]],
                "cost_usd": res["cost_usd"],
                "latency_s": res["latency_s"],
            }
            if q["category"] != "out_of_scope" and not res["refused"]:
                row["judge"] = judge(q, res)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            done[q["id"]] = row
            time.sleep(EVAL_PAUSE)

    rows = [done[q["id"]] for q in questions if q["id"] in done]
    print("\n" + build_report(rows, args.name))


if __name__ == "__main__":
    main()