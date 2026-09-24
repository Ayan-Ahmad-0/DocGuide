import re

CITE_RE = re.compile(r"\[([^\[\]]*?(?:Article|Recital)[^\[\]]*?)\]")
LABEL_RE = re.compile(r"^(Article|Recital)\s+(\d+)(?:\((\d+)\))?(?:\s*-\s*\((\d+)\))?")


def extract_citations(answer: str) -> list[str]:
    cites = []
    for m in CITE_RE.finditer(answer):
        for part in re.split(r"\s*[;,]\s*(?=(?:Article|Recital)\b)", m.group(1)):
            cites.append(part.strip())
    return cites


def parse_label(label: str):
    m = LABEL_RE.match(label.strip())
    if not m:
        return None
    kind, num, p, q = m.groups()
    p = int(p) if p else None
    q = int(q) if q else p
    return kind, int(num), p, q


def _coverage(chunk_labels: list[str]) -> dict:
    cov = {}
    for lab in chunk_labels:
        parsed = parse_label(lab)
        if parsed:
            kind, num, p, q = parsed
            cov.setdefault((kind, num), []).append(None if p is None else (p, q))
    return cov


def find_unsupported(cites: list[str], chunk_labels: list[str]) -> list[str]:
    """Citations that do not correspond to any retrieved passage."""
    cov = _coverage(chunk_labels)
    bad = []
    for c in dict.fromkeys(cites):
        parsed = parse_label(c)
        if not parsed:
            bad.append(c)
            continue
        kind, num, p, q = parsed
        ranges = cov.get((kind, num))
        if not ranges:
            bad.append(c)
            continue
        if p is None or None in ranges:   # article-level cite, or chunk without paragraph info
            continue
        if not all(any(a <= n <= b for a, b in ranges) for n in range(p, min(q, p + 50) + 1)):
            bad.append(c)
    return bad