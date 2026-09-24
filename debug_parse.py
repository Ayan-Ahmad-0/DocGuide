import re
from config import RAW_HTML
from src.parse import html_to_lines, merge_markers, find_line

html = RAW_HTML.read_text(encoding='utf-8', errors='replace')
lines = merge_markers(html_to_lines(html))
for prefix in ['Whereas','HAVE ADOPTED THIS REGULATION','This Regulation shall be binding']:
    try:
        idx = find_line(lines, prefix)
        print(prefix, idx, repr(lines[idx][:200]))
    except Exception as e:
        print(prefix, 'ERR', e)

# print some article-like lines around the article section
start = find_line(lines, 'HAVE ADOPTED THIS REGULATION')
end = find_line(lines, 'This Regulation shall be binding', start)
print('range', start, end)
for i in range(start, min(start + 200, end)):
    if 'Article' in lines[i] or 'CHAPTER' in lines[i] or 'Section' in lines[i] or 'This' in lines[i]:
        print(i, repr(lines[i]))
