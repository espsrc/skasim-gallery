#!/usr/bin/env python3
"""Extract figures and metadata from a skasim weblog.html.

The weblog embeds every figure as a base64 PNG and every setting as a
<th>/<td> table. This script writes the PNGs under readable names and dumps
all metadata to JSON, so a gallery page can be written from facts rather
than guesses.

    python extract_weblog.py WEBLOG.html --prefix meerkat --out case5-foo/images
    python extract_weblog.py WEBLOG.html --list        # inspect, write nothing

Output names:
    {prefix}_layout.png, {prefix}_uv_coverage.png,
    {prefix}_sky_model.png, {prefix}_sky_model_fov.png
    {prefix}[_{tag}]_{dirty_image|model|clean|residual|psf}.png
The imaging tag (e.g. wsclean-stokes-v -> stokes_v) is only inserted when
the weblog holds more than one product of the same kind.

Metadata goes to {out}/{prefix}_weblog.json (or stdout with --list).
Stdlib only.
"""

import argparse
import base64
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

PLOT_TITLES = {
    "telescope layout": "layout",
    "uv coverage": "uv_coverage",
    "full sky model": "sky_model",
    "sky model (fov zoom)": "sky_model_fov",
}
FIG_CAPTIONS = {
    "dirty image": "dirty_image",
    "dirty": "dirty_image",
    "model": "model",
    "clean": "clean",
    "restored": "clean",
    "residual": "residual",
    "psf": "psf",
}


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


class WeblogParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.div_stack = []  # (classes, id)
        self.h2 = None
        self.header = {"lines": []}
        self.sections = {}  # h2 -> list of tables
        self.products = {}  # tag -> {name, imager, stats, table}
        self.images = []  # dicts: data, kind, label, panel
        self._capture = None  # (kind, buffer)
        self._pending_img = None
        self._pending_title = None
        self._table = None
        self._row = None
        self._cell = None

    # -- helpers ---------------------------------------------------------
    def _panel(self):
        for _, ident in reversed(self.div_stack):
            if ident and ident.startswith("panel-"):
                return ident[len("panel-"):]
        return None

    def _in_class(self, name):
        return any(name in classes for classes, _ in self.div_stack)

    def _start_capture(self, kind):
        self._capture = (kind, [])

    # -- parser hooks ----------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "div":
            classes = (a.get("class") or "").split()
            self.div_stack.append((classes, a.get("id")))
            if "plot-title" in classes:
                self._start_capture("plot-title")
            elif "stats-line" in classes:
                self._start_capture("stats")
            elif self._in_class("header") and "header" not in classes:
                self._start_capture("header-line")
        elif tag in ("h1", "h2"):
            self._start_capture(tag)
        elif tag == "figcaption":
            self._start_capture("figcaption")
        elif tag == "strong" and self._panel() and not self._table:
            self._start_capture("product-name")
        elif tag == "span" and "badge" in (a.get("class") or "") and self._panel():
            self._start_capture("imager")
        elif tag == "img":
            src = a.get("src", "")
            m = re.match(r"data:image/(\w+);base64,(.*)", src, re.S)
            if m:
                self._flush_pending_img()
                img = {"data": m.group(2), "ext": m.group(1), "alt": a.get("alt", ""),
                       "panel": self._panel(), "section": self.h2}
                if self._pending_title:
                    img["kind"] = self._pending_title
                    self._pending_title = None
                    self.images.append(img)
                else:
                    self._pending_img = img  # label arrives with <figcaption>
        elif tag == "table":
            self._table = []
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in ("th", "td") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if self._capture and (
            (tag == "div" and self._capture[0] in ("plot-title", "stats", "header-line"))
            or tag == {"h1": "h1", "h2": "h2", "figcaption": "figcaption",
                       "product-name": "strong", "imager": "span"}.get(self._capture[0])
        ):
            kind, buf = self._capture
            text = clean("".join(buf))
            self._capture = None
            panel = self._panel()
            if kind == "h2":
                self.h2 = text
            elif kind == "h1":
                # the status badge sits inside the <h1>, flush against the run id
                m = re.match(r"(.*?)(completed|failed|running|partial)?$", text)
                self.header["run"] = m.group(1)
                self.header["status"] = m.group(2) or ""
            elif kind == "header-line" and text:
                self.header["lines"].append(text)
            elif kind == "plot-title":
                self._pending_title = PLOT_TITLES.get(text.lower(), slug(text))
            elif kind == "stats" and panel:
                self.products.setdefault(panel, {})["stats"] = text
            elif kind == "product-name" and panel:
                self.products.setdefault(panel, {}).setdefault("name", text)
            elif kind == "imager" and panel:
                self.products.setdefault(panel, {}).setdefault("imager", text)
            elif kind == "figcaption" and self._pending_img:
                self._pending_img["kind"] = FIG_CAPTIONS.get(text.lower(), slug(text))
                self.images.append(self._pending_img)
                self._pending_img = None
        if tag == "div" and self.div_stack:
            self.div_stack.pop()
        elif tag in ("th", "td") and self._cell is not None:
            self._row.append(clean("".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            self._store_table(self._table)
            self._table = None

    def handle_data(self, data):
        if self._capture:
            self._capture[1].append(data)
        if self._cell is not None:
            self._cell.append(data)

    def _flush_pending_img(self):
        """An image with no <figcaption> (e.g. inside a table cell) is named by its alt text."""
        if self._pending_img:
            self._pending_img["kind"] = slug(self._pending_img["alt"]) or "image"
            self.images.append(self._pending_img)
            self._pending_img = None

    def _store_table(self, rows):
        panel = self._panel()
        kv = all(len(r) == 2 for r in rows)
        table = dict(rows) if kv else rows
        if panel:
            self.products.setdefault(panel, {})["settings"] = table
        else:
            self.sections.setdefault(self.h2 or "preamble", []).append(table)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def product_slug(tag):
    """wsclean-stokes-v -> stokes_v ; wsclean-r-0 -> r_0 ; dirty -> dirty."""
    s = re.sub(r"^(wsclean|oskar|dirty)[-_]?", "", tag) or tag
    return slug(s)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("weblog", type=Path)
    ap.add_argument("--prefix", default="", help="filename prefix, e.g. the telescope or run id")
    ap.add_argument("--out", type=Path, help="output directory for PNGs and JSON")
    ap.add_argument("--list", action="store_true", help="print what would be extracted, write nothing")
    args = ap.parse_args()

    p = WeblogParser()
    p.feed(args.weblog.read_text(encoding="utf-8", errors="replace"))
    p._flush_pending_img()

    # decide names; add the product tag only where a kind repeats
    counts = {}
    for img in p.images:
        if img["panel"]:
            counts[img["kind"]] = counts.get(img["kind"], 0) + 1
    pre = f"{args.prefix}_" if args.prefix else ""
    for img in p.images:
        parts = [img["kind"]]
        if img["panel"] and counts[img["kind"]] > 1:
            parts.insert(0, product_slug(img["panel"]))
        img["file"] = f"{pre}{'_'.join(parts)}.{img['ext']}"

    header = dict(p.header)
    lines = header.pop("lines")
    if lines:
        header["meta"] = lines[0]
        header["title"] = lines[1] if len(lines) > 1 else ""
        header["description"] = " ".join(lines[2:])

    meta = {
        "source": str(args.weblog),
        "header": header,
        "sections": p.sections,
        "products": p.products,
        "images": [{k: v for k, v in i.items() if k != "data"} for i in p.images],
    }

    if args.list or not args.out:
        json.dump(meta, sys.stdout, indent=2, ensure_ascii=False)
        print()
        return

    args.out.mkdir(parents=True, exist_ok=True)
    for img in p.images:
        (args.out / img["file"]).write_bytes(base64.b64decode(img["data"]))
    meta_path = args.out / f"{pre}weblog.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    for img in p.images:
        print(f"  {img['file']:<45} {img['section'] or ''} / {img['panel'] or '-'}")
    print(f"  {meta_path.name:<45} metadata")


if __name__ == "__main__":
    main()
