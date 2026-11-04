"""Add width/height and loading="lazy" to every raster <img> of a gallery page, in place.

    python img_sizes.py caseN-<slug>/index.html

Sizes come from the image files, so run it after the figures are final (and again if they change).
Images that already carry the attribute, SVGs and the empty lightbox image are left alone.
"""
import re
import sys
from pathlib import Path

from PIL import Image

IMG = re.compile(r"<img\b(.*?)/?>", re.S)


def fix_page(page):
    page = Path(page)

    def fix(m):
        tag, attrs = m.group(0), m.group(1)
        src = re.search(r'src="([^"]+)"', attrs)
        if not src:
            return tag
        f = page.parent / src.group(1)
        add = []
        if "width=" not in attrs and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and f.exists():
            w, h = Image.open(f).size
            add += [f'width="{w}"', f'height="{h}"']
        if "loading=" not in attrs:
            add.append('loading="lazy"')
        if not add:
            return tag
        end = tag.rstrip("/>").rstrip()
        if "\n" in tag:  # keep one attribute per line
            indent = re.search(r"\n(\s*)\S", tag).group(1)
            return end + "".join(f"\n{indent}{a}" for a in add) + "\n" + indent[:-4] + "/>"
        return end + " " + " ".join(add) + " />"

    page.write_text(IMG.sub(fix, page.read_text()))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        fix_page(p)
