import sys
from bs4 import BeautifulSoup
from config import RAW_HTML

sys.stdout.reconfigure(encoding="utf-8")
html = RAW_HTML.read_text(encoding="utf-8", errors="replace")
print("size:", len(html))
print("first 300 chars:", html[:300].replace("\n", " "))

soup = BeautifulSoup(html, "lxml")
text = soup.get_text("\n")
print("has 'Whereas':", "Whereas" in text)
print("has 'HAVE ADOPTED':", "HAVE ADOPTED THIS REGULATION" in text)
print("has 'Article 5':", "Article 5" in text)
print("id sample:", [t.get("id") for t in soup.find_all(id=True)][:15])
print("class sample:", sorted({c for t in soup.find_all(class_=True) for c in t["class"]})[:30])