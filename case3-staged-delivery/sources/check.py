import re
with open('weblog_05.html', 'r') as f: content = f.read()
# Let's find img tags and their previous text to identify them
tags = re.findall(r'<img\s+([^>]+)>', content)
for i, tag in enumerate(tags):
    if 'data:image' in tag:
        print(f"Image {i+1}: base64, len {len(tag)}")
    else:
        print(f"Image {i+1}: {tag}")
