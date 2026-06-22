import re

with open('weblog_05.html', 'r') as f:
    content = f.read()

# Find all occurrences of <img> or <a> tags that contain the images
# The pipeline might wrap images in <a> tags with titles.
matches = re.finditer(r'<a[^>]*data-title="([^"]*)"[^>]*>[\s\n]*<img', content)
for i, match in enumerate(matches):
    print(f"Image {i+1} title: {match.group(1)}")

