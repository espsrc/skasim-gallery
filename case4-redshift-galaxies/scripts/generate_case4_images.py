"""
Generate the combined redshift-sequence figure for skasim-gallery Case 4.

Reads FITS outputs for Arp 220 at z = 0.018, 0.15, 0.30, 0.50, 1.00, 2.00
in bands 2 (1.35 GHz), 5a (~6.5 GHz) and 5b (~11.9 GHz) and produces a
3 x 6 panel figure with:
- shared intensity range per row
- one colorbar per row
- synthesized beam ellipse in the bottom-left of each panel
- adaptive physical scale bar in the bottom-right
- 3x upsampling zoom to avoid blocky pixels
"""

from pathlib import Path
from astropy.io import fits
from astropy.cosmology import Planck18
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams, gridspec, patches
from scipy.ndimage import zoom
import matplotlib.patheffects as path_effects


rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Sora', 'DejaVu Sans']

# paths relative to this script
REPO_ROOT = Path(__file__).resolve().parents[3]
CASE_DIR = REPO_ROOT / 'portfolio' / 'case4-redshift-galaxies'
SRC_DIR = CASE_DIR / 'sources'
IMG_DIR = CASE_DIR / 'images'
IMG_DIR.mkdir(exist_ok=True)

# configuration
BANDS = [
    # (row label, file tag, vmin, vmax)
    # NOTE: manual values captured here for rollback reference.
    # Previous auto/fixed values: 1.35GHz auto 0.1282, band5a fixed 0.005769326690289384, band5b fixed 0.0027.
    ('Band 2 (1.35 GHz)', '1.35GHz', None, 0.04269475764314328),
    ('Band 5a (6.5 GHz)', 'band5a', -0.000023865611709981953, 0.0012),
    ('Band 5b (11.9 GHz)', 'band5b', -0.0000441096400587122, 0.0027),
]
REDSHIFTS = [0.15, 0.30, 0.50, 1.00, 2.00]
ZOOM_FACTOR = 3  # upsample before cropping back to original pixel dimensions


def adaptive_scale_bar(z, px_per_kpc, min_px=25, max_px=180):
    """Choose a round kpc length whose on-screen bar is readable.

    Candidates are tested in order and the one closest to ~80 px is returned.
    """
    candidates = [0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100]
    best = None
    for length_kpc in candidates:
        px = length_kpc * px_per_kpc
        if min_px <= px <= max_px:
            if best is None or abs(px - 80) < abs(best[1] - 80):
                best = (length_kpc, px)
    if best is None:
        length_kpc = 1.0
        best = (length_kpc, length_kpc * px_per_kpc)
    return best


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
    return upsampled[y0:y0+ny, x0:x0+nx]


def add_beam(ax, header, nx, ny, beam_size_factor=1.0):
    """Draw synthesized beam ellipse in bottom-left corner.

    The position angle is inverted relative to the header BPA as requested.
    """
    cdelt1 = abs(header['CDELT1'])
    cdelt2 = abs(header['CDELT2'])
    bmaj_pix = header['BMAJ'] / cdelt1 * beam_size_factor
    bmin_pix = header['BMIN'] / cdelt2 * beam_size_factor
    bpa = -header['BPA']
    cx, cy = 0.08 * nx, 0.08 * ny
    for ec, lw in [('black', 3), ('white', 1.5)]:
        ell = patches.Ellipse(
            (cx, cy), width=bmaj_pix, height=bmin_pix, angle=bpa,
            edgecolor=ec, facecolor='none', linewidth=lw, transform=ax.transData
        )
        ax.add_patch(ell)


def add_scale_bar(ax, header, z, nx, ny, fixed_px=None):
    """Draw physical scale bar in the bottom-right corner.

    If fixed_px is given, the bar is exactly that many pixels long and the
    physical length in kpc is computed from the redshift. Otherwise an adaptive
    round length is chosen.
    """
    arcsec_per_px = abs(header['CDELT1']) * 3600.0
    kpc_per_arcsec = Planck18.kpc_proper_per_arcmin(z).value / 60.0
    kpc_per_px = kpc_per_arcsec * arcsec_per_px

    if fixed_px is not None:
        length_px = fixed_px
        length_kpc = length_px * kpc_per_px
        label = f'{length_kpc:.2f} kpc' if length_kpc < 1 else f'{length_kpc:.1f} kpc'
    else:
        px_per_kpc = 1.0 / kpc_per_px
        length_kpc, length_px = adaptive_scale_bar(z, px_per_kpc)
        label = f'{length_kpc:g} kpc'

    x1 = 0.72 * nx
    yb = 0.08 * ny
    x2 = x1 + length_px
    for ec, lw in [('black', 3), ('white', 1.5)]:
        ax.plot([x1, x2], [yb, yb], color=ec, linewidth=lw, solid_capstyle='butt')

    t = ax.text(
        (x1 + x2) / 2, yb - 0.02 * ny, label,
        fontsize=9, color='white', ha='center', va='top', fontweight='bold'
    )
    t.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black')])


def auto_vmax(path):
    data, _ = load_fits(path)
    flat = np.abs(data.ravel())
    flat = flat[np.isfinite(flat)]
    return float(np.percentile(flat, 99.5))


def main():
    fig = plt.figure(figsize=(16, 9))
    gs = gridspec.GridSpec(
        3, 6, figure=fig, wspace=0.04, hspace=0.02,
        width_ratios=[1, 1, 1, 1, 1, 0.06]
    )

    for row, (label, tag, vmin, vmax) in enumerate(BANDS):
        if vmax is None:
            vmax = auto_vmax(SRC_DIR / f'run_arp220_{tag}_aastar_image.fits')
            vmin = 0.0

        axes_row = []
        for col, z in enumerate(REDSHIFTS):
            ax = fig.add_subplot(gs[row, col])
            axes_row.append(ax)

            zstr = f'{z:.2f}'
            suffix = f'_z{zstr}'
            path = SRC_DIR / f'run_arp220_{tag}{suffix}_aastar_image.fits'

            data, header = load_fits(path)
            data = zoom_crop(data, ZOOM_FACTOR)
            ny, nx = data.shape

            im = ax.imshow(data, origin='lower', cmap='inferno', vmin=vmin, vmax=vmax)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)

            # redshift label, top-right
            txt = ax.text(
                0.97, 0.97, f'z = {zstr}', transform=ax.transAxes,
                fontsize=11, color='white', fontweight='bold', ha='right', va='top'
            )
            txt.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black')])

            add_beam(ax, header, nx, ny)
            if tag == '1.35GHz':
                add_scale_bar(ax, header, z, nx, ny, fixed_px=100)
            else:
                add_scale_bar(ax, header, z, nx, ny, fixed_px=200)

        axes_row[0].set_ylabel(
            label, fontsize=10, rotation=90, ha='center', va='center', labelpad=20
        )

        # per-row colorbar
        cax = fig.add_subplot(gs[row, 5])
        cbar = fig.colorbar(im, cax=cax, orientation='vertical')
        cbar.ax.tick_params(labelsize=8)
        cbar.set_label('Jy/beam', fontsize=8, rotation=90, labelpad=4)

    plt.tight_layout(pad=0.2)
    out = IMG_DIR / 'arp220_redshift_sequence_combined.png'
    fig.savefig(out, dpi=150, bbox_inches='tight', pad_inches=0.05, facecolor='white')
    plt.close(fig)
    print('saved', out)


if __name__ == '__main__':
    main()
