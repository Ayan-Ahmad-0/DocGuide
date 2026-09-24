import json
import re
from bs4 import BeautifulSoup
from config import RAW_HTML, DOCUMENTS, SOURCE_URL


def html_to_lines(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style"]):
        t.decompose()
    text = soup.get_text("\n").replace("\xa0", " ")
    lines = [re.sub(r"\s+", " ", l).strip() for l in text.split("\n")]
    return [l for l in lines if l]


def merge_markers(lines: list[str]) -> list[str]:
    """Table layouts put '1.' or '(a)' on its own line; glue it to the next line."""
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        if re.fullmatch(r"\d{1,2}\.|\([a-z]{1,3}\)|\([ivx]{1,4}\)", l) and i + 1 < len(lines):
            out.append(l + " " + lines[i + 1])
            i += 2
        else:
            out.append(l)
            i += 1
    return out


def find_line(lines: list[str], prefix: str, start: int = 0) -> int:
    for i in range(start, len(lines)):
        if lines[i].upper().startswith(prefix.upper()):
            return i
    raise ValueError(f"Marker not found in file: {prefix!r}. Run scripts/inspect_html.py")


def record(type_, number, title, text, chapter=None) -> dict:
    return {
        "id": f"{type_}-{number}",
        "type": type_,
        "number": number,
        "title": title,
        "chapter": chapter,
        "text": text.strip(),
        "source_url": SOURCE_URL,
    }


def parse_recitals(lines: list[str]) -> list[dict]:
    out, num, buf = [], 0, []
    for l in lines:
        m = re.match(r"^\((\d{1,3})\)\s*(.*)$", l)
        if m and int(m.group(1)) == num + 1:
            if num:
                out.append(record("recital", num, None, " ".join(buf)))
            num = int(m.group(1))
            buf = [m.group(2)] if m.group(2) else []
        elif num:
            buf.append(l)
    if num:
        out.append(record("recital", num, None, " ".join(buf)))
    return out


def parse_articles(lines: list[str]) -> list[dict]:
    out, chapter, cur, i = [], None, None, 0

    def close():
        if cur and cur["body"]:
            out.append(record("article", cur["number"], cur["title"],
                              "\n".join(cur["body"]), cur["chapter"]))

    while i < len(lines):
        l = lines[i]
        m = re.match(r"^Article\s+(\d{1,3})(?:[.:])?\s*(.*)$", l)
        expected = cur["number"] + 1 if cur else 1
        if m:
            num = int(m.group(1))
            title = m.group(2).strip()
            if num == expected:
                close()
                cur = {"number": num, "title": title or "", "chapter": chapter, "body": []}
                i += 1
                if not title and i < len(lines) and lines[i] and not re.match(r"^(Article|CHAPTER|Section)\b", lines[i]):
                    cur["title"] = lines[i]
                    i += 1
                continue
        if re.match(r"^CHAPTER [IVX]+$", l) and i + 1 < len(lines):
            chapter = f"{l} - {lines[i + 1]}"   # applies to the NEXT articles
            i += 2
        elif re.match(r"^Section \d+$", l) and i + 1 < len(lines):
            i += 2                               # skip section heading + title
        else:
            if cur:
                cur["body"].append(l)
            i += 1
    close()
    return out


def parse(html: str) -> list[dict]:
    lines = merge_markers(html_to_lines(html))
    r0 = find_line(lines, "Whereas")
    a0 = find_line(lines, "HAVE ADOPTED THIS REGULATION", r0)
    a1 = find_line(lines, "This Regulation shall be binding", a0)
    return parse_recitals(lines[r0 + 1:a0]) + parse_articles(lines[a0 + 1:a1])


def main():
    html = RAW_HTML.read_text(encoding="utf-8")
    docs = parse(html)
    DOCUMENTS.parent.mkdir(parents=True, exist_ok=True)
    with DOCUMENTS.open("w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"Wrote {len(docs)} records to {DOCUMENTS}")


if __name__ == "__main__":
    main()