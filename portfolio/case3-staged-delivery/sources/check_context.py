import re

with open('weblog_05.html', 'r') as f:
    content = f.read()

matches = re.finditer(r'<img\s', content)
for match in matches:
    start = max(0, match.start() - 100)
    print(f"Image context: {content[start:match.start()].strip()}")
