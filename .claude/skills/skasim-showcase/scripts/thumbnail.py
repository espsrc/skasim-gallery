"""Gallery-card thumbnails: 4:3, no axes, no labels, no colour bars, no beams.

Two entry points:

    # from an array (FITS plane, moment map, ...)
    from thumbnail import bare
    bare(data, "caseN-<slug>/images/thumbnail.png", cmap="viridis", vmin=..., vmax=...)

    # from a matplotlib PNG that already has axes (e.g. a weblog image)
    python thumbnail.py crop images/meerkat_clean.png images/thumbnail.png [--center X Y] [--zoom Z]

The card crops to 4:3 with object-fit: cover, so anything drawn at another
aspect loses its edges; produce 4:3 here and nothing is cut.
"""
import argparse

import numpy as np

W, H = 800, 600  # output size in pixels


def _fit_box(x0, y0, x1, y1, center=None, zoom=1.0):
    """Largest 4:3 box inside (x0, y0, x1, y1), shrunk by `zoom`, around `center`."""
    w, h = x1 - x0, y1 - y0
    bw = min(w, h * 4 / 3) / zoom
    bh = bw * 3 / 4
    cx, cy = center if center else ((x0 + x1) / 2, (y0 + y1) / 2)
    cx = min(max(cx, x0 + bw / 2), x1 - bw / 2)
    cy = min(max(cy, y0 + bh / 2), y1 - bh / 2)
    return int(cx - bw / 2), int(cy - bh / 2), int(cx + bw / 2), int(cy + bh / 2)


def bare(data, out, center=None, zoom=1.0, origin="lower", **imshow_kw):
    """Render a 2-D array edge to edge at 4:3. `center` is (x, y) in array pixels."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ny, nx = data.shape
    if center is not None and origin == "lower":
        center = (center[0], ny - 1 - center[1])
    img = data[::-1] if origin == "lower" else data
    x0, y0, x1, y1 = _fit_box(0, 0, nx, ny, center, zoom)
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img[y0:y1, x0:x1], origin="upper", aspect="auto", interpolation="nearest", **imshow_kw)
    ax.set_axis_off()
    fig.savefig(out, dpi=100, bbox_inches=None, pad_inches=0)
    plt.close(fig)


def _axes_frame(rgb):
    """Pixel box of the main axes frame: the two longest dark lines each way."""
    dark = rgb[..., :3].max(axis=2) < 90
    ny, nx = dark.shape
    cols = np.where(dark.sum(axis=0) > 0.5 * ny)[0]
    rows = np.where(dark.sum(axis=1) > 0.5 * nx)[0]
    if len(cols) < 2 or len(rows) < 2:
        raise SystemExit("no axes frame found; pass an array to bare() instead")
    # the colour bar adds frame lines beside the map; the main frame is the widest gap
    i, j = np.argmax(np.diff(cols)), np.argmax(np.diff(rows))
    return cols[i], rows[j], cols[i + 1], rows[j + 1]


def crop(src, out, center=None, zoom=1.0, inset=4):
    """Cut the data area out of a PNG with axes and save it at 4:3."""
    from PIL import Image

    im = Image.open(src).convert("RGB")
    x0, y0, x1, y1 = _axes_frame(np.asarray(im))
    box = _fit_box(x0 + inset, y0 + inset, x1 - inset, y1 - inset, center, zoom)
    im.crop(box).resize((W, H), Image.LANCZOS).save(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("crop")
    c.add_argument("src")
    c.add_argument("out")
    c.add_argument("--center", nargs=2, type=float, help="x y in source PNG pixels")
    c.add_argument("--zoom", type=float, default=1.0)
    a = ap.parse_args()
    crop(a.src, a.out, a.center, a.zoom)
