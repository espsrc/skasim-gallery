---
name: skasim-showcase
description: Build a new science-case page for the skasim gallery from skasim weblogs, FITS products or notes, matching the existing cases' look and feel, and register it on the gallery index and README. Use when adding, drafting or showcasing a new skasim science case, or turning a skasim run/weblog into a gallery page.
---

# skasim-showcase

A science case is a folder `caseN-<slug>/` laid out as described in the repo's `CLAUDE.md` (`index.html`, `images/`, `sources/`, `config/`). Every page is the same static, self-contained HTML: shared palette and fonts, a stack of white `case-block` cards, a closing `takeaways` card, and a lightbox for results. Skill files, relative to this one:

- `assets/template.html`: the canonical page. It carries the full stylesheet for every component, the lightbox and the layout toggle, so each new page starts as a copy of it.
- `components.md`: snippet for each block (settings tables, result cards, layout toggle, source cards, equations, summary table) and when to pick it. Read it at step 4.
- `scripts/extract_weblog.py`: pulls the embedded PNGs and every metadata table out of a skasim `weblog.html`. Stdlib only.
- `scripts/img_sizes.py`: adds `width`/`height` and `loading="lazy"` to every image on a page, read from the image files.
- `scripts/thumbnail.py`: makes the 4:3 gallery-card thumbnail, either from an array (`bare()`) or by cutting the data area out of a weblog PNG that has axes (`crop`).
- `scripts/web_style.py`: the matplotlib look for every figure drawn for the gallery (site palette, Inter type, panel-name pills). Import it in place of any paper style.

## Steps

### 1. Gather the inputs

Collect from the user: the weblog(s) or run directory, the science question, which telescope(s)/band(s), references to cite, and who supplied any sky model (name, affiliation, ORCID). Also ask for the case slug and title if they are not obvious. The next case number is one more than the highest `caseN-` folder at the repo root.

Done when you hold every weblog the page will show, and the user has stated the science question in their own words.

### 2. Extract figures and facts

Copy each weblog to `caseN-<slug>/sources/` and each run's config to `caseN-<slug>/config/`, cleaned as `CLAUDE.md` describes. Then, per weblog:

```bash
python .claude/skills/skasim-showcase/scripts/extract_weblog.py caseN-<slug>/sources/weblog.html --list      # inspect
python .claude/skills/skasim-showcase/scripts/extract_weblog.py caseN-<slug>/sources/weblog.html --prefix <run> --out caseN-<slug>/images
```

`--prefix` names the run (`meerkat`, `AA2`, `stokes`); outputs are `<run>_layout.png`, `<run>_uv_coverage.png`, `<run>_sky_model[_fov].png`, `<run>[_<product>]_{clean,model,residual,dirty_image}.png` and `<run>_weblog.json`. Delete the PNGs the page will not show, and delete the `*_weblog.json` files once the page is written: `sources/` keeps the originals.

When the inputs are FITS or catalogues rather than weblogs (case2, case4 pattern), write a plotting script under `caseN-<slug>/scripts/` (git-ignored) and draw in the gallery's web style, not a paper style such as `plot-like-bordiu`. Copy `scripts/web_style.py` beside the script and start with:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent))
from web_style import plt, label, style_colorbar, ACCENT, BORDER, MUTED, TEXT
```

What the style expects of the figure (`case2-polarization/scripts/` shows it in use, in a local checkout only, since `scripts/` folders are git-ignored):

- **Panel names** go inside the top-left corner with `label(ax, "Stokes V")`. No titles above the panels.
- **Colour bars** get `style_colorbar(cb, "mJy/beam")`. Keep labels short: `RA`, `Dec`, `mJy/beam`, `V / σ$_V$`.
- **Markers and labels** for targets use `ACCENT` on light backgrounds and white on dark ones such as viridis. Zoom boxes and inset frames use `TEXT`.
- **Colour maps:** `viridis` for total-intensity (Stokes I) maps unless the user asks otherwise, `Blues` for a catalogue scaled by flux, and continuous `RdBu_r` for signed maps such as Stokes V or residuals.
- **Zooms** go in a corner inset (`ax.inset_axes`), with a thin rectangle on the parent panel showing where they come from.
- **Gallery thumbnail:** never from the plotting axes. Call `thumbnail.bare()` from `scripts/thumbnail.py` on the array, which gives 4:3 with no axes (see step 5).
- **Output:** PNG at 170–200 dpi. The style already sets a white background and a tight bounding box.

Done when every number the page will quote (frequency, bandwidth, obs time, stations, beam, peak, RMS, SNR, robust) is in a JSON or table you can point to.

### 3. Plan the page

Choose the section sequence from the case's shape; the existing cases are the precedents:

| Shape | Sections | Precedent |
|---|---|---|
| One run, one message | Science motivation · Simulation run (`spec-table`) · Sky model · Results · Takeaways | case2 |
| Same field, several telescopes | Science motivation · Simulation runs (`runs-table`) · Sky model · Results (cards + layout toggle) · Takeaways | case1 |
| Progression of arrays/epochs | Introduction & Strategy · one block per stage · Takeaways + `summary-table` | case3 |
| Model-driven sweep | Physical motivation · model (`equation-box`) · Input image models (`source-grid`) · Simulation runs (`run-grid`) · Results (`wide-figure`) · Beyond the current model · Takeaways | case4 |

Show the user the chosen sections and the figures going into each before writing HTML. Done when the user has approved the outline.

### 4. Write the page

Copy `assets/template.html` to `caseN-<slug>/index.html`, replace every `{{…}}`, and fill each `<!-- COMPONENT -->` from `components.md`. The template's `<head>` carries the search and sharing metadata; fill it as follows:

- **Description** (`{{DESCRIPTION}}`, used five times: meta, `og:`, `twitter:` and the JSON-LD): 140–160 characters naming telescope, band, target and the result, e.g. *"A 2 h SKA-Low simulation at 175 MHz of 60 462 T-RECS sources: two faint, 80% circularly polarized sources are recovered blindly in Stokes V at +8.1σ and −6.3σ."*
- **URLs** (canonical, `og:url`, JSON-LD) use the folder form `…/caseN-<slug>/`. Links between pages keep `index.html` (`../index.html`, `../caseN-<slug>/index.html`) so the site still works when opened from disk.
- **JSON-LD** (`TechArticle`): `about` gets 4–6 topics as one `{"@type": "Thing", "name": …}` object each (telescope, science topic, technique); `citation` lists the `https://doi.org/…` URL of every paper cited on the page, and is dropped when there are none. `author` and `publisher` stay the CSIC4SKA organisation; the gallery credits no individual authors. Leave the `Organization` and `SoftwareSourceCode` entries as they are.
- **Dates**: `datePublished` and `dateModified` in the JSON-LD and the two `<time>` elements in the byline under the facts strip. On a new page both are today; when a page changes later, update `dateModified`, the byline's *Updated* date and the page's `<lastmod>` in `sitemap.xml`.
- **Social image**: the 800×600 `thumbnail.png` from step 5; nothing else to make. The page loads `../assets/case-nav.css` and `../assets/case-nav.js` from the repo root. They build the contents sidebar from the `<h2>` of each `case-block` and add previous/next links, so keep section headings short. Add `data-toc="Short label"` to an `<h2>` whose text is too long for the sidebar. Remove the `<!-- MATHJAX -->` block when the page has no equations. Keep the template's CSS whole so components stay consistent across cases.

House style for the prose, taken from the existing pages:

- **Voice**: write with the `write-like-bordiu` skill.
- **Lead**: 2–4 sentences naming telescope, band, field and the question, ending on the result when the case has one. Search engines and AI assistants quote this paragraph, so it must stand on its own.
- **Acronyms**: spell each out once, in the lead or at first use: *the Square Kilometre Array (SKA)*, *the Tiered Radio Extragalactic Continuum Simulation (T-RECS)*, *neutral hydrogen (HI)*, *the Karl G. Jansky Very Large Array (VLA)*.
- **Facts strip** (`<ul class="facts">` under the lead): exactly three items: the telescope(s) in `<strong>`, the band (SKA-Mid band number or L-band; a frequency only where the telescope has no named bands, e.g. SKA-Low), and the target object(s) or field. No observing times, field sizes, run counts, redshift or inclination ranges, or results; those belong in the body.
- **Numbers**: quote weblog values exactly (`Peak 2.447 mJy/beam · RMS 5.63 µJy/beam · SNR 434.8`), with typographic units: `µJy`, `″`, `°`, `×`, `–` for ranges, `·` as separator.
- **Telescope names** as skasim prints them: `SKA-LOW-AAstar`, `SKA-MID-AA*`, `SKA1-MID`, `MeerKAT`, `VLA B`.
- **Citations** inline, linked to the DOI: `(<a href="https://doi.org/…">Author et al. YEAR</a>)`; fall back to `Author et al. YEAR, arXiv:XXXX.XXXXX` only when there is no DOI. Check each DOI resolves to the paper you mean; never write one from memory. Every DOI also goes in the JSON-LD `citation` list.
- **Takeaways**: 3–5 bullets, each opening with a `<strong>` claim followed by the evidence from this run.
- **Alt text** on every image; `data-caption` on every result card with its full stats.

Once the figures are final, run `python .claude/skills/skasim-showcase/scripts/img_sizes.py caseN-<slug>/index.html` to give every image its size and lazy loading.

Done when no `{{` remains (`grep -n '{{' caseN-<slug>/index.html` is empty), every `src` resolves to a file in `images/`, and every `<img>` with a `src` has `width`, `height` and `loading`.

### 5. Register the case

- `index.html` (repo root): add a card at the end of `.case-grid`, copying the existing card markup. It needs:
  - `href="caseN-<slug>/index.html"`
  - the thumbnail `caseN-<slug>/images/thumbnail.png`
  - a `<div class="chips">` with three chips: telescope as `chip scope` (`SKA-Low`, `SKA-Mid`, `Multi-array`), then band, then the capability shown (`Stokes V`, `Spectral line`, `Redshift`). Keep each chip to one or two words so the three fit on one line of a card.
  - `<h3>Case #N — Title</h3>`
  - a 40–55-word `<p>` naming telescope, band, field and the hook
- **Thumbnail**: 4:3 with **no axes, ever**: no ticks, labels, colour bars, beams, panel names or titles, just the data edge to edge. Make it with `scripts/thumbnail.py`: `bare(array, out, ...)` when you have the data (FITS, moment map), or `python thumbnail.py crop <weblog.png> <out>` to cut the data area out of an image that has axes. Pass `center`/`zoom` so the interesting structure fills the card. A wide-field noise map reads as nothing at card size, so zoom in on the detection.
- `assets/case-nav.js` (repo root): append `{ dir: "caseN-<slug>", title: "Short title" }` to `CASES`. That list drives the previous/next links on every case page.
- `README.md`: add a row to the *Current cases* table (Case · Telescope · Key capability · Status).
- `sitemap.xml` (repo root): add `<url><loc>https://espsrc.github.io/skasim-gallery/caseN-<slug>/</loc><lastmod>YYYY-MM-DD</lastmod></url>`, and bump the homepage's `<lastmod>`.
- `llms.txt` (repo root): add a bullet under *Science cases* in the same form as the others: linked `Case N — Title`, then one sentence with telescope, band, setup and result, numbers included.
- `index.html` FAQ: the answer to *What do the science cases show?* lists every case and states their number; add the new one. Keep the `FAQPage` JSON-LD in `<head>` word for word in step with it (same text, tags stripped).

Done when the new card, the `CASES` entry, the README row, the sitemap entry and the `llms.txt` bullet sit after the previous case, and the FAQ counts the new case.

### 6. Verify

Open the page with the `run` skill or a local server (`python -m http.server` from the repo root) and check: fonts load, every image renders, each result card opens the lightbox and arrows cycle through all cards, layout toggles open and close, and the layout holds at phone width. Check the gallery card links to the page and the page's "Back to cases" returns to the grid. The contents sidebar should appear at 1280 px wide and highlight the section being read, previous/next should link the neighbouring cases, and the card should look right in both the grid and list views of the gallery.

Also check the metadata: every `<script type="application/ld+json">` block on the page and on `index.html` parses as JSON (`python -c "import json,re,sys; [json.loads(b) for b in re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', open(sys.argv[1]).read(), re.S)]" caseN-<slug>/index.html`), the description is 140–160 characters, and the canonical URL matches the sitemap entry.

Done when every check above passes; report any that fail rather than skipping them.

## Keep the review artifact in sync

`review/` at the repo root (git-ignored, so it may be missing in a fresh clone) holds a private claude.ai artifact where the user comments on the text of every case: `build.py` and `template.html` make `index.html` from the case pages, `files.json` lists the figures it shows, and `ARTIFACT_URL` holds its link. Each block carries a number such as `1·5.3` (case 1, section 5, block 3), and comments may quote it.

Whenever a case page, its figures, or its gallery card changes, through this skill or any other edit, and `review/` exists:

1. Run `python3 review/build.py`.
2. Publish `review/index.html` with the Artifact tool to the URL in `review/ARTIFACT_URL`, passing every entry of `review/files.json` as `files` so new or redrawn figures upload. Pass `null` for a figure the pages no longer use. If this conversation has not published or read the artifact yet, read it first (`action: "read"`), as the tool requires. Never publish without `url`: that makes a second artifact.

When the user asks to apply the review comments: read them with `ArtifactComments` (`action: "read"`, the same URL), edit the case pages, rebuild and republish as above, then reply to and resolve each thread you addressed. Threads not sent to Claude cannot be resolved by you; list them for the user. Block numbers shift once text moves, so match a comment to its passage by the quoted text, and by the number only as a fallback.
