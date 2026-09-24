import json
from config import DOCUMENTS


def load():
    return [json.loads(l) for l in DOCUMENTS.open(encoding="utf-8")]


def test_counts():
    docs = load()
    assert sum(d["type"] == "article" for d in docs) == 99
    assert sum(d["type"] == "recital" for d in docs) == 173


def test_every_record_has_metadata():
    for d in load():
        assert d["number"] > 0 and d["text"].strip() and d["id"]


def test_no_leading_number_in_recitals():
    for d in load():
        if d["type"] == "recital":
            assert not d["text"].startswith("(")