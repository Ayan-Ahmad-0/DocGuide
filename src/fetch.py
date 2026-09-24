import sys
import requests
from config import RAW_HTML, SOURCE_URL

HEADERS = {"User-Agent": "Mozilla/5.0 (DocGuide portfolio project)"}


def fetch(url: str = SOURCE_URL) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    html = resp.text
    # Sanity check: a real GDPR page has recital/article containers
    if 'id="rct_1"' not in html or 'id="art_1"' not in html:
        raise RuntimeError(
            f"Got HTTP {resp.status_code} but not the real document "
            "(probably a bot-challenge page). Open the URL in your browser, "
            f"Save Page As -> HTML, and put it at {RAW_HTML}"
        )
    return html


def main():
    RAW_HTML.parent.mkdir(parents=True, exist_ok=True)
    try:
        html = fetch()
    except Exception as e:
        print(f"Fetch failed: {e}", file=sys.stderr)
        sys.exit(1)
    RAW_HTML.write_text(html, encoding="utf-8")
    print(f"Saved {len(html):,} chars to {RAW_HTML}")


if __name__ == "__main__":
    main()