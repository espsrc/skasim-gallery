"""Matplotlib look for gallery figures: matches the site palette and sans type."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from glob import glob  # noqa: E402
from matplotlib import font_manager  # noqa: E402

for _f in glob("/usr/share/fonts/opentype/inter/Inter-*.otf"):
    font_manager.fontManager.addfont(_f)

TEXT = "#1c1917"
MUTED = "#78716c"
BORDER = "#d6d3d1"
ACCENT = "#0d7c72"  # teal, as the site theme (assets/theme-teal.css)

plt.rcParams.update({
    "font.family": ["Inter", "DejaVu Sans"],
    "font.size": 11,
    "text.color": TEXT,
    "axes.labelcolor": MUTED,
    "axes.edgecolor": BORDER,
    "axes.linewidth": 0.8,
    "axes.labelsize": 11,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.size": 3.5,
    "ytick.major.size": 3.5,
    "legend.frameon": False,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
})


def label(ax, text):
    """Panel name inside the top-left corner, in a soft white pill."""
    ax.text(0.03, 0.97, text, transform=ax.transAxes, ha="left", va="top",
            fontsize=11, fontweight="semibold", color=TEXT,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                      edgecolor=BORDER, linewidth=0.8, alpha=0.92))


def style_colorbar(cb, text):
    cb.set_label(text, color=MUTED)
    cb.outline.set_edgecolor(BORDER)
    cb.ax.tick_params(color=BORDER, labelcolor=MUTED, length=3)
