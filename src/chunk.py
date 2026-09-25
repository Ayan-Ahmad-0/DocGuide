import json
import re
import sys
from config import DOCUMENTS, CHUNKS, MAX_WORDS, MIN_WORDS

PARA = re.compile(r"^(\d{1,2})\.\s")     # "1. Personal data shall be:"
DEFN = re.compile(r"^\((\d{1,2})\)(?:\s|$)")   # Article 4 definitions: "(1) 'personal data'..."
FOOTNOTE = re.compile(r"^(\(\d+\)\s*)?OJ [LC]\b")


# Topic glosses for clauses that are mostly lists of article numbers.
# Keyed by (article_number, paragraph_label). Extend as more weak spots surface.
REFERENCE_GLOSS = {
    (83, "4"): "includes failures to appoint or properly involve a data protection officer "
               "(Article 37 DPO designation, Article 38 DPO position, Article 39 DPO tasks), "
               "and other Articles 25 to 39 obligations",
    (83, "5"): "includes violations of data subject rights, international data transfer rules, "
               "and basic processing principles",
}


def add_reference_gloss(doc: dict, labels: list, embed_text: str) -> str:
    """Append a short topic gloss to embed_text for clauses that are dense
    article-number cross-references, so they embed closer to topical queries."""
    if doc["type"] != "article":
        return embed_text
    for label in labels:
        gloss = REFERENCE_GLOSS.get((doc["number"], label))
        if gloss:
            return f"{embed_text}\n(Note: {gloss})"
    return embed_text
def wc(text: str) -> int:
    return len(text.split())


def clean(text: str) -> str:
    lines = [l for l in text.split("\n") if not FOOTNOTE.match(l.strip())]
    return "\n".join(lines).strip()


def split_units(doc: dict) -> list[tuple]:
    """Split a document into (paragraph_label, text) units."""
    text = clean(doc["text"])
    if doc["type"] == "recital":
        return [(None, text)]

    pattern = DEFN if doc["number"] == 4 else PARA
    units, label, buf, last = [], None, [], 0
    for line in text.split("\n"):
        m = pattern.match(line)
        if m and int(m.group(1)) == last + 1:   # only accept the next number in sequence
            if buf:
                units.append((label, "\n".join(buf)))
            last = int(m.group(1))
            label, buf = str(last), [line]
        else:
            buf.append(line)
    if buf:
        units.append((label, "\n".join(buf)))
    return units


def split_long(text: str) -> list[str]:
    """Break an oversized unit at line/sentence boundaries."""
    if wc(text) <= MAX_WORDS:
        return [text]
    pieces = [p for p in re.split(r"\n|(?<=[.;:])\s+", text) if p.strip()]
    out, cur = [], []
    for p in pieces:
        if cur and wc(" ".join(cur)) + wc(p) > MAX_WORDS:
            out.append(" ".join(cur))
            cur = []
        cur.append(p)
    if cur:
        out.append(" ".join(cur))
    return out


def citation(doc: dict, labels: list) -> str:
    if doc["type"] == "recital":
        return f"Recital {doc['number']}"
    paras = [l for l in labels if l]
    n = doc["number"]
    if not paras:
        return f"Article {n}"
    first, last = paras[0], paras[-1]
    return f"Article {n}({first})" if first == last else f"Article {n}({first})-({last})"


def build_chunks(doc: dict) -> list[dict]:
    parts = []
    for label, text in split_units(doc):
        for piece in split_long(text):
            parts.append({"labels": [label], "text": piece})

    merged = []
    for p in parts:   # merge small pieces forward
        if merged and wc(merged[-1]["text"]) < MIN_WORDS \
                and wc(merged[-1]["text"]) + wc(p["text"]) <= MAX_WORDS:
            merged[-1]["text"] += "\n" + p["text"]
            merged[-1]["labels"] += p["labels"]
        else:
            merged.append(p)
    # a tiny last chunk joins the one before it
    if len(merged) > 1 and wc(merged[-1]["text"]) < MIN_WORDS \
            and wc(merged[-2]["text"]) + wc(merged[-1]["text"]) <= MAX_WORDS:
        last = merged.pop()
        merged[-1]["text"] += "\n" + last["text"]
        merged[-1]["labels"] += last["labels"]

    chunks = []
    for i, m in enumerate(merged):
        cite = citation(doc, m["labels"])
        header = f"GDPR {cite}"
        if doc["title"]:
            header += f" - {doc['title']}"
        if doc.get("chapter"):
            header += f" ({doc['chapter']})"
        chunks.append({
            "chunk_id": f"{doc['id']}-c{i}",
            "doc_id": doc["id"],
            "type": doc["type"],
            "number": doc["number"],
            "title": doc["title"],
            "chapter": doc.get("chapter"),
            "citation": cite,
            "text": m["text"],
            "embed_text": add_reference_gloss(
                doc, m["labels"], f"{header}\n{m['text']}"
            ),
            "words": wc(m["text"]),
        })
    return chunks


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    docs = [json.loads(l) for l in DOCUMENTS.open(encoding="utf-8")]
    chunks = [c for d in docs for c in build_chunks(d)]
    with CHUNKS.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    words = [c["words"] for c in chunks]
    print(f"{len(docs)} documents -> {len(chunks)} chunks")
    print(f"words per chunk: min {min(words)}, avg {sum(words)//len(words)}, max {max(words)}")
    for t in ("article", "recital"):
        print(f"  {t}: {sum(c['type'] == t for c in chunks)} chunks")


if __name__ == "__main__":
    main()