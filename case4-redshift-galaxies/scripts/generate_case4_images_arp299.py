"""
Generate the combined redshift-sequence figure for skasim-gallery Case 4 (Arp 299).

Reads FITS outputs for Arp 299 at z = 0.010944, 0.15, 0.30, 0.50, 1.00, 2.00
in bands 2 (1.35 GHz), 5a (~6.5 GHz) and 5b (~11.9 GHz) and produces a
3 x 6 panel figure with:
- shared intensity range per row for the high-z (inferno) panels
- dedicated, less noisy viridis stretch for the native low-z panel
- one colorbar per row in uJy/beam
- synthesized beam ellipse in the bottom-left of each panel
- physical scale bar in the bottom-right, fixed in original-image pixels
- upsampling zoom to avoid blocky pixels
"""

from pathlib import Path

import matplotlib
import numpy as np
from astropy.cosmology import Planck18
from astropy.io import fits

matplotlib.use("Agg")
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from matplotlib import gridspec, patches, rcParams
from scipy.ndimage import zoom

rcParams["font.family"] = "sans-serif"
rcParams["font.sans-serif"] = ["Sora", "DejaVu Sans"]

# paths relative to this script
REPO_ROOT = Path(__file__).resolve().parents[3]
CASE_DIR = REPO_ROOT / "portfolio" / "case4-redshift-galaxies"
SRC_DIR = CASE_DIR / "sources_arp299"
IMG_DIR = CASE_DIR / "images"
IMG_DIR.mkdir(exist_ok=True)

# (row label, file tag,
#  low-z vmin, low-z vmax, low-z cmap,
#  high-z vmin, high-z vmax)
BANDS = [
    ("Band 2 (1.35 GHz)", "1.35GHz", 0.0, 0.005, "viridis", 0.0, 0.0018),
    ("Band 5a (6.5 GHz)", "band5a", 0.000005, 0.0003, "viridis", 0.000001, 0.000085),
    (
        "Band 5b (11.9 GHz)",
        "band5b",
        0.0000015,
        0.00009,
        "viridis",
        0.0000003,
        0.000025,
    ),
]
REDSHIFTS = [0.15, 0.30, 0.50, 1.00, 2.00]
ZOOM_FACTOR_LOW_Z = 1.5  # no longer used, kept for reference
ZOOM_FACTOR_HIGH_Z = 5.5  # stronger zoom for higher redshifts


def load_fits(path):
    with fits.open(path) as hdul:
        data = hdul[0].data
        header = hdul[0].header
    if data.ndim > 2:
        data = data.squeeze()
    return data, header


def zoom_crop(data, factor):
    ny, nx = data.shape
    upsampled = zoom(data, factor, order=1)
    zny, znx = upsampled.shape
    y0 = (zny - ny) // 2
    x0 = (znx - nx) // 2
    return upsampled[y0 : y0 + ny, x0 : x0 + nx]


def add_beam(ax, header, nx, ny, beam_size_factor=1.0):
    """Draw synthesized beam ellipse in bottom-left corner."""
    cdelt1 = abs(header["CDELT1"])
    cdelt2 = abs(header["CDELT2"])
    bmaj_pix = header["BMAJ"] / cdelt1 * beam_size_factor
    bmin_pix = header["BMIN"] / cdelt2 * beam_size_factor
    bpa = -header["BPA"]
    cx, cy = 0.08 * nx, 0.08 * ny
    for ec, lw in [("black", 3), ("white", 1.5)]:
        ell = patches.Ellipse(
            (cx, cy),
            width=bmaj_pix,
            height=bmin_pix,
            angle=bpa,
            edgecolor=ec,
            facecolor="none",
            linewidth=lw,
            transform=ax.transData,
        )
        ax.add_patch(ell)


def add_scale_bar(ax, header, z, nx, ny, zoom_factor=1.0, fixed_px=100):
    """Draw a physical scale bar in the bottom-right corner.

    `fixed_px` is the bar length in original-image pixels. Because the image has
    been upsampled by `zoom_factor` before cropping, the same physical length
    appears as `fixed_px * zoom_factor` on the final displayed panel.
    """
    arcsec_per_px = abs(header["CDELT1"]) * 3600.0
    kpc_per_arcsec = Planck18.kpc_proper_per_arcmin(z).value / 60.0
    kpc_per_px = kpc_per_arcsec * arcsec_per_px

    length_kpc = fixed_px * kpc_per_px
    label = f"{length_kpc:.2f} kpc" if length_kpc < 1 else f"{length_kpc:.1f} kpc"

    # in the zoomed/cropped panel, the same physical length is longer in screen px
    length_px_screen = fixed_px * zoom_factor

    x1 = 0.72 * nx
    yb = 0.08 * ny
    x2 = x1 + length_px_screen
    for ec, lw in [("black", 3), ("white", 1.5)]:
        ax.plot([x1, x2], [yb, yb], color=ec, linewidth=lw, solid_capstyle="butt")

    t = ax.text(
        (x1 + x2) / 2,
        yb - 0.02 * ny,
        label,
        fontsize=9,
        color="white",
        ha="center",
        va="top",
        fontweight="bold",
    )
    t.set_path_effects([path_effects.withStroke(linewidth=2, foreground="black")])


def superscript(n: int) -> str:
    """Return a Unicode superscript string for an integer exponent."""
    mapping = {
        "0": "⁰",
        "1": "¹",
        "2": "²",
        "3": "³",
        "4": "⁴",
        "5": "⁵",
        "6": "⁶",
        "7": "⁷",
        "8": "⁸",
        "9": "⁹",
        "-": "⁻",
    }
    return "".join(mapping[c] for c in str(n))


def format_colorbar_with_exponent_ujy(cbar, vmin: float, vmax: float) -> None:
    """Label colorbar ticks in uJy/beam with a single shared 10^exp on top."""
    if not np.isfinite(vmax) or vmax == 0.0:
        return

    # convert Jy/beam -> uJy/beam for display
    u_vmax = vmax * 1e6
    u_vmin = vmin * 1e6

    exp = int(np.floor(np.log10(abs(u_vmax))))
    scale = 10.0**exp
    norm_max = u_vmax / scale
    norm_min = u_vmin / scale

    # choose a nice step in normalized units, aim for 4-6 ticks
    span = norm_max - norm_min
    steps = [0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5, 10]
    step = next((s for s in steps if span / s <= 6), 10)

    t0 = np.floor(norm_min / step) * step
    ticks_norm = np.arange(t0, norm_max + step * 1e-6, step)
    ticks_norm = ticks_norm[
        (ticks_norm >= norm_min - 1e-12) & (ticks_norm <= norm_max + 1e-12)
    ]
    if len(ticks_norm) == 0:
        ticks_norm = np.array([norm_min, norm_max])
    if ticks_norm[-1] < norm_max - 1e-12:
        ticks_norm = np.append(ticks_norm, norm_max)

    ticks = ticks_norm * scale / 1e6  # back to Jy/beam for colorbar
    labels = []
    for i, tn in enumerate(ticks_norm):
        # show one decimal if needed, else integer
        if abs(tn - round(tn)) < 1e-9:
            label = f"{int(round(tn)):d}"
        else:
            label = f"{tn:g}"
        if i == len(ticks_norm) - 1:
            label += f"×10{superscript(exp)}"
        labels.append(label)

    cbar.set_ticks(ticks)
    cbar.set_ticklabels(labels)
    cbar.ax.tick_params(labelsize=8)
    cbar.set_label("μJy/beam", fontsize=8, rotation=90, labelpad=4)


def main():
    fig = plt.figure(figsize=(16, 9))
    gs = gridspec.GridSpec(
        3,
        6,
        figure=fig,
        wspace=0.04,
        hspace=0.02,
        width_ratios=[1, 1, 1, 1, 1, 0.06],
    )

    for row, (
        label,
        tag,
        low_z_vmin,
        low_z_vmax,
        low_z_cmap,
        high_z_vmin,
        high_z_vmax,
    ) in enumerate(BANDS):
        axes_row = []
        for col, z in enumerate(REDSHIFTS):
            ax = fig.add_subplot(gs[row, col])
            axes_row.append(ax)

            zstr = f"{z:.2f}"
            suffix = f"_z{zstr}"
            path = SRC_DIR / f"run_Arp299_{tag}{suffix}_aastar_image.fits"

            data, header = load_fits(path)
            data = zoom_crop(data, ZOOM_FACTOR_HIGH_Z)
            ny, nx = data.shape

            vmin, vmax, cmap = high_z_vmin, high_z_vmax, "inferno"

            im = ax.imshow(data, origin="lower", cmap=cmap, vmin=vmin, vmax=vmax)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)

            txt = ax.text(
                0.97,
                0.97,
                f"z = {zstr}",
                transform=ax.transAxes,
                fontsize=11,
                color="white",
                fontweight="bold",
                ha="right",
                va="top",
            )
            txt.set_path_effects(
                [path_effects.withStroke(linewidth=2, foreground="black")]
            )

            add_beam(ax, header, nx, ny)
            add_scale_bar(ax, header, z, nx, ny, zoom_factor=ZOOM_FACTOR_HIGH_Z, fixed_px=100)

        axes_row[0].set_ylabel(
            label, fontsize=10, rotation=90, ha="center", va="center", labelpad=20
        )

        cax = fig.add_subplot(gs[row, 5])
        cbar = fig.colorbar(im, cax=cax, orientation="vertical")
        format_colorbar_with_exponent_ujy(cbar, high_z_vmin, high_z_vmax)

    plt.tight_layout(pad=0.2)
    out = IMG_DIR / "arp299_redshift_sequence_combined.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close(fig)
    print("saved", out)


if __name__ == "__main__":
    main()
