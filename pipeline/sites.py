"""Build sites.json: published points where they exist, else the best-lit pixel of each PGDA site box.

Run once (needs network): python sites.py
"""
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import from_bounds

from horizon import R_MOON

PGDA = "/vsicurl/https://pgda.gsfc.nasa.gov/data"
ILLUM = f"{PGDA}/MoonIllumination/AVGVISIB_75S_120M_201608.TIF"
OUT = Path(__file__).resolve().parent / "sites.json"

PUBLISHED = [
    ("connecting-ridge", "Connecting Ridge", -89.53432, 209.94767, "LPSC 2024 abstract 1695"),
    ("peak-near-shackleton", "Peak near Shackleton", -89.01701, 126.27302, "LPSC 2024 abstract 1695"),
    ("mons-mouton", "Mons Mouton", -84.528, 30.719, "LPSC 2025 abstract 2742"),
]
BOXES = [  # PGDA LOLA 5 m/px site folders (Barker et al. 2021)
    ("shackleton-rim", "Shackleton Rim", "Site04"),
    ("nobile-rim-1", "Nobile Rim 1", "Site06"),
    ("de-gerlache-rim", "de Gerlache Rim", "Site11"),
    ("leibnitz-beta", "Leibnitz Beta Plateau", "Site20"),
    ("malapert-massif", "Malapert Massif", "Site23"),
    ("haworth", "Haworth", "Haworth"),
    ("nobile-rim-2", "Nobile Rim 2", "DM2"),
]


def to_latlon(x, y):
    rho = np.hypot(x, y)
    return float(np.degrees(2 * np.arctan(rho / (2 * R_MOON))) - 90), float(np.degrees(np.arctan2(x, y)) % 360)


def best_lit(folder):
    with rasterio.open(f"{PGDA}/LOLA_5mpp/{folder}/{folder}_final_adj_5mpp_surf.tif") as d:
        b = d.bounds
    with rasterio.open(ILLUM) as m:
        win = from_bounds(*b, transform=m.transform)
        a = m.read(1, window=win, masked=True)
        r, c = np.unravel_index(np.argmax(a), a.shape)
        x, y = rasterio.transform.xy(m.window_transform(win), r, c)
    lat, lon = to_latlon(x, y)
    return lat, lon, float(a[r, c]) * 4e-5  # DN scaling from the PDS label


def main():
    sites = [dict(id=i, name=n, lat=la, lon=lo, source=s) for i, n, la, lo, s in PUBLISHED]
    for sid, name, folder in BOXES:
        lat, lon, ill = best_lit(folder)
        sites.append(dict(id=sid, name=name, lat=round(lat, 5), lon=round(lon, 5),
                          source=f"Best-lit 120 m pixel (PGDA mean solar-disc visibility {ill:.0%}) in PGDA LOLA 5 m site box {folder}"))
    OUT.write_text(json.dumps(sites, indent=2))
    for s in sites:
        print(s["id"], s["lat"], s["lon"])


if __name__ == "__main__":
    main()
