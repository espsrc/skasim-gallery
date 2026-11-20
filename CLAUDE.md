# skasim-gallery

Static site (GitHub Pages, no build step) showcasing science cases simulated with `skasim`. To build or update a case page, use the `skasim-showcase` skill.

## Case folder layout

`caseN-<slug>/` holds:

- `index.html`: the page.
- `images/`: only the figures the page shows. Delete unused PNGs and extraction JSONs.
- `sources/`: the original skasim weblogs. Tracked but never linked from the page. FITS-based cases keep their inputs here as git-ignored files, or have no `sources/`.
- `config/`: the skasim configs that produced the page, one per run (subfolders when there are many, e.g. case 4 by band).

Local only, git-ignored: `*/scripts/` (plotting scripts), `*/backup_*/`, `*/sources_v*/`, all FITS, and large sky models (e.g. case 2's `sky_model_64ch_2h.json`).

## Configs

The originals live on the `skasim` host (`ssh skasim`) under `/mnt/scratch/cbordiu/espsrc_ska_simulator/configs/`, and each run writes `run_manifest.json` (with the config it actually ran) under `/mnt/scratch/cbordiu/skasim-executions/`. When copying a config into `config/`:

1. Check it against the run's `run_manifest.json`, and check that the run is the one behind the page's images. Server configs are sometimes edited after the run: case 5's live configs had moved to a different channel grid.
2. Set `title` to `Case #N — <page title>`, plus a run qualifier when the case has several runs.
3. Rewrite `description` from the config's actual settings (frequency, band, channels, time, robust, iterations, mgain). Don't trust the old text.
4. Make paths generic: inputs → `data/<file>`, `output_dir` → `output/<run name>`. Leave skasim-internal paths such as `sefd_file` as they are. Finally, grep the result for `/mnt`, `cbordiu` and `../`.
