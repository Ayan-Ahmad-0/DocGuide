import json
from config import DOCUMENTS, EVAL_QUESTIONS


def test_questions_are_valid():
    doc_ids = {json.loads(l)["id"] for l in DOCUMENTS.open(encoding="utf-8")}
    qs = [json.loads(l) for l in EVAL_QUESTIONS.open(encoding="utf-8") if l.strip()]
    ids = [q["id"] for q in qs]
    assert len(ids) == len(set(ids))
    for q in qs:
        assert q["category"] in {"answerable", "partial", "out_of_scope"}
        assert q["question"].strip() and q["reference"].strip()
        if q["category"] == "out_of_scope":
            assert q["expected_docs"] == []
        else:
            assert q["expected_docs"] and set(q["expected_docs"]) <= doc_ids