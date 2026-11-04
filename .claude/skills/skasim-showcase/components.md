# Case-page components

Every component below is already styled in `assets/template.html`. Pick by the shape of the case, paste the snippet inside a `<div class="case-block">`, and fill it from the extracted weblog JSON. The "used in" line names the existing page to open when you want to see it rendered in context.

## Settings: pick one per page

**`spec-table`**: a single run. Two columns, one row per setting. Used in: case2.

```html
<table class="spec-table">
    <tr><th>Setting</th><th>Value</th></tr>
    <tr><td>Facility</td><td>SKA-LOW-AAstar</td></tr>
    <tr><td>Frequency / bandwidth</td><td>300 MHz · 200 MHz (16 × 12.5 MHz)</td></tr>
    <tr><td>Observation time</td><td>1200 s · 150 × 8 s integrations</td></tr>
    <tr><td>Image / pixel</td><td>512 × 512 · 0.4922″/px · FoV 0.07°</td></tr>
    <tr><td>Weighting</td><td>Briggs robust 0</td></tr>
</table>
```

**`runs-table`**: 2–5 matched runs compared side by side, one column per run. Follow it with a `<p class="note">` for shared settings (phase centre, image size). Used in: case1.

```html
<div class="runs-table-wrap">
    <table class="runs-table">
        <thead>
            <tr><th>Parameter</th><th>MeerKAT</th><th>SKA1-MID</th></tr>
        </thead>
        <tbody>
            <tr><th>Dish / Antennas</th><td>13.5 m · 64</td><td>15.0 m · 144</td></tr>
            <tr><th>Beam</th><td>5.0″ × 3.3″, PA 145.8°</td><td>3.6″ × 3.1″, PA 144.0°</td></tr>
        </tbody>
    </table>
</div>
<p class="note" style="margin-top: 18px">Phase centre RA 150.075385°, Dec +2.218322°. Image size 2048 × 2048 pixels at 0.3516 arcsec, FoV 0.2°.</p>
```

**`run-grid`**: a parameter sweep (many runs that differ along one or two axes), summarised as themed cards rather than one column per run. Used in: case4.

```html
<div class="run-grid">
    <div class="run-card">
        <h4>Observation</h4>
        <dl>
            <dt>Snapshot length</dt><dd>10 minutes</dd>
            <dt>Bands</dt><dd>1.35, 6.5 &amp; 11.9 GHz</dd>
        </dl>
    </div>
    <!-- 3–4 cards: Telescope, Observation, <sweep axis>, Products -->
</div>
```

## Figures

**`wide-figure`**: one full-width static image (sky model, a combined multi-panel sequence). Used in: case1, case2, case4.

```html
<figure class="wide-figure">
    <img src="images/X.png" alt="…" />
    <figcaption>…</figcaption>
</figure>
```

**`fig-grid`**: several small static images in a row (layout + uv coverage).

```html
<div class="fig-grid">
    <figure><img src="images/X_layout.png" alt="…" /><figcaption>Telescope layout</figcaption></figure>
    <figure><img src="images/X_uv_coverage.png" alt="…" /><figcaption>UV coverage</figcaption></figure>
</div>
```

**`result-card`** in a `result-grid`: the zoomable imaging results, two per row. Every card joins one lightbox gallery across the page, so the page must keep the lightbox markup and script from the template. `data-caption` carries the full stats; `.beam` carries the short line under the thumbnail. Used in: case1, case2, case3.

```html
<div class="result-grid">
    <div
        class="result-card"
        data-lightbox="images/X_clean.png"
        data-caption="Stokes V restored image — Peak 152.19 µJy/beam · RMS 399.68 nJy/beam · SNR 380.8 · Beam 19.181″ × 11.555″"
    >
        <figure>
            <img src="images/X_clean.png" alt="Stokes V restored image" />
            <figcaption>Stokes V circular polarization</figcaption>
        </figure>
        <div class="beam">Peak 152.19 µJy/beam · RMS 399.68 nJy/beam · SNR 380.8</div>
    </div>
</div>
```

**Layout toggle**: add to a `result-card` when runs differ by array, so the reader can open that run's layout and uv coverage in place. Each panel needs a unique `id`. Used in: case1.

```html
        <div class="beam">Beam 5.0″ × 3.3″, PA 145.8° · Robust -2</div>
        <button class="check-layout" onclick="event.stopPropagation(); toggleLayout('layout-meerkat');">Check layout →</button>
        <div id="layout-meerkat" class="layout-panel">
            <div class="fig-grid">
                <figure><img src="images/meerkat_layout.png" alt="MeerKAT telescope layout" /><figcaption>Telescope layout</figcaption></figure>
                <figure><img src="images/meerkat_uv_coverage.png" alt="MeerKAT uv coverage" /><figcaption>UV coverage</figcaption></figure>
            </div>
        </div>
    </div>
```

**Per-run blocks**: when the case is a progression (array assemblies, epochs), give each run its own `case-block` with an `<h2>`, one paragraph, and a two-card `result-grid` (layout + restored image). Close with a `summary-table` in the takeaways. Used in: case3.

## Inputs and physics

**`source-card`** in a `source-grid`: input image models or templates, image on top and a short description below. Used in: case4.

```html
<div class="source-grid">
    <article class="source-card">
        <img src="images/arp220_image.png" alt="Radio model image of Arp 220" />
        <div class="source-body">
            <h4>Arp 220</h4>
            <p>Late-stage ULIRG merger; distance ≈ 78 Mpc; IR-based SFR ≈ 200 M<sub>⊙</sub> yr<sup>−1</sup>.</p>
        </div>
    </article>
</div>
```

**`equation-box`**: display maths via MathJax. Keep the `<!-- MATHJAX -->` block in `<head>` only when the page uses this. Interleave short `<p>` lines that say what each equation does. Used in: case4.

```html
<div class="equation-box">
    <p>The apparent size is set by the angular-diameter distance:</p>
    \[ \theta(z) = \theta(z_0)\,\frac{D_A(z_0)}{D_A(z)} . \]
</div>
```

**ORCID credit**: credit whoever supplied a sky model inline, right after their name.

```html
Jane Doe <a class="orcid-symbol" href="https://orcid.org/0000-0000-0000-0000" aria-label="Jane Doe ORCID" title="Jane Doe ORCID">iD</a> (IAA-CSIC)
```

## Summary

**`summary-table`**: numbers per run (stations, RMS, beam) at the end of the takeaways, under `<h3 style="margin-top: 42px">Performance Summary</h3>` and a one-line `<p>` saying how values were measured. Used in: case3.

```html
<table class="summary-table">
    <thead><tr><th>Assembly</th><th>Stations</th><th>RMS (μJy/beam)</th><th>Beam (arcsec)</th></tr></thead>
    <tbody>
        <tr><td>AA0.5</td><td>4</td><td>177.52</td><td>12.35</td></tr>
    </tbody>
</table>
```
