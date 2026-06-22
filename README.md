# skasim-gallery

A curated collection of examples and real-world science cases built with
[`skasim`](https://github.com/espsrc/espsrc_ska_simulator).  Each case in this repository is a
self-contained reference that shows a concrete capability of the simulator using the actual config and
catalog files needed to reproduce it.

> **Status:** early-stage gallery.  More cases and outputs will be added as the
> simulator evolves.

## What this is

- Reference science cases powered by `skasim`.
- Fully runnable configs and source catalogs.
- Output images and weblog summaries, where available.
- A practical starting point for users who want to see what the simulator can do
  before writing their own configs from scratch.

## Current cases

| Case | Telescope | Key capability | Status |
|------|-----------|----------------|--------|
| MIGHTEE deep field | MeerKAT / SKA1-MID / VLA | Deep continuum survey, source confusion, and image-fidelity comparison | complete |
| Polarization in the confusion limit | SKA-LOW | Stokes V detection of a polarized source in a crowded 0.07° field; auroral/SPI science case | complete |
| SKAO staged delivery | SKA1-MID AA0.5 → AA4 | SDC1 field observed across five array assemblies (Band 2, 950–1670 MHz) | complete |
| Arp 299 / redshift coverage | SKA1-MID | Multi-frequency study of an interacting galaxy system | placeholder |

## See also

- [`skasim`](https://github.com/espsrc/espsrc_ska_simulator) — the simulator that powers
  every case in this gallery.
- [skasim documentation / config examples](...)
