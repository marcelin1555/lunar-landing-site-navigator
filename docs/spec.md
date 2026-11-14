# Lunar Landing Site Navigator — spec

Team Quiral Labs, NASA Space Apps 2026, challenge "Lunar Landing Site Navigator".

## Goal
Help a mission planner compare lunar south-pole landing sites by **when the Sun and the Earth are visible**, taking the real local horizon (terrain) into account.

## Users
1. Mission planner (primary): compares sites and dates.
2. Public and educators (only if time allows).

## Data
- Terrain: LOLA polar DEM `LDEM_75S_120M` (PDS, 120 m/px, polar stereographic, heights relative to a 1737.4 km sphere).
- Ephemerides: NAIF SPICE kernels `de440s.bsp`, `moon_pa_de440_200625.bpc`, `moon_de440_250416.tf`, `naif0012.tls`, `pck00011.tpc`.
- Validation: the PGDA average illumination and Earth-visibility maps (product 69), and JPL Horizons for the Sun's elevation.

## Pipeline (Python, offline)
1. `horizon.py`: 360° horizon profile per site, built by ray marching along great circles on the DEM with exact 3D geometry, so lunar curvature is included. Observer height is 2 m.
2. `ephemeris.py`: azimuth and elevation of the Sun and the Earth at the site, using the MOON_ME frame and light time plus stellar aberration (`LT+S`).
3. `visibility.py`:
   - Fraction of the Sun's disk above the local horizon.
   - Earth center above the horizon.
4. `summarize.py`: percentage of time sunlit, percentage with Earth visible, longest dark period, and next sunset and Earthset.
5. `export.py`: writes one JSON per site to `web/public/data/`, plus `sites.json`.

Time window: 2026-11-01 to 2028-12-31, hourly.

## Front end (Svelte + TS + D3, static)
- Site list.
- Skyline chart showing the horizon plus the Sun and Earth paths.
- Visibility timeline.
- Summary cards.
- Comparison table.
- The default date is now.

## Rules
- Energy is shown as hours of sunlight, never in watts.
- Every number carries its source and limits: a 120 m DEM, no refraction, and the Sun disk treated as a uniform circle.

## Known limitations
- The 120 m DEM smooths nearby terrain (under about 1 km). The 5 m PGDA DEMs are a possible upgrade for near-field terrain.
- The DEM uses the DE421 MOON_ME frame, while the ephemerides are DE440. The difference is tens of meters, which is negligible for the horizon.

## AI use
AI assistance (Claude) was used for research, architecture discussion, and code generation and review. All design decisions, data validation, and final review were done by the author. This is declared in the README.
