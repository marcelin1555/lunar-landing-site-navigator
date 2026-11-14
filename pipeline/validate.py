"""Compare our sunlit / Earth-visible % with the PGDA average maps (Mazarico et al. 2011) and write docs/validation.md.

PGDA averages cover 18.6 years (a full lunar nodal cycle); ours cover Nov 2026 to Dec 2028,
so a few percentage points of difference are expected. Run after export.py (needs network).
"""
import json
from pathlib import Path

import numpy as np
import rasterio

from horizon import stereo_south

ROOT = Path(__file__).resolve().parent.parent
MAPS = "/vsicurl/https://pgda.gsfc.nasa.gov/data/MoonIllumination/AVGVISIB_75S_120M_201608{}.TIF"
SCALE = 4e-5  # DN scaling from the PDS labels


def pgda_value(path, lat, lon):
    with rasterio.open(path) as m:
        x, y = stereo_south(lat, lon)
        return float(next(m.sample([(x, y)]))[0]) * SCALE * 100


def main():
    sites = json.loads((ROOT / "web/public/data/sites.json").read_text())["sites"]
    rows = ["| Site | Sunlit, ours | Sunlit, PGDA | Δ | Earth, ours | Earth, PGDA | Δ |", "|---|---:|---:|---:|---:|---:|---:|"]
    ds, de = [], []
    for s in sites:
        sun = pgda_value(MAPS.format(""), s["lat"], s["lon"])
        earth = pgda_value(MAPS.format("_EARTH"), s["lat"], s["lon"])
        a, b = s["summary"]["sunlit_pct"], s["summary"]["earth_visible_pct"]
        ds.append(a - sun)
        de.append(b - earth)
        rows.append(f"| {s['name']} | {a:.1f}% | {sun:.1f}% | {a - sun:+.1f} | {b:.1f}% | {earth:.1f}% | {b - earth:+.1f} |")
    rows.append(f"\nMean absolute difference: sunlit {np.mean(np.abs(ds)):.1f} pts, Earth {np.mean(np.abs(de)):.1f} pts.")
    text = "# Validation against PGDA average maps\n\n" + __doc__.split("\n\n")[1] + "\n\n" + "\n".join(rows) + "\n"
    (ROOT / "docs/validation.md").write_text(text, encoding="utf-8")
    print(rows[-1].strip())


if __name__ == "__main__":
    main()
