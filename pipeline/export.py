"""Run the pipeline for every site and write one JSON per site for the web app.

Usage: python export.py [site-id ...]
"""
import json
import sys
from pathlib import Path

import numpy as np
import spiceypy as sp

import ephemeris as eph
from horizon import horizon, load_lola_polar, sample
from summarize import summarize
from visibility import earth_visible, sun_fraction

ROOT = Path(__file__).resolve().parent.parent
DEM_PATH = ROOT / "data" / "raw" / "ldem_75s_120m.img"
OUT_DIR = ROOT / "web" / "public" / "data"
START, END, STEP_S = "2026-11-01T00:00", "2028-12-31T23:00", 3600
OBS_HEIGHT = 2.0
N_AZ = 720


def r2(a):
    return np.round(np.asarray(a, dtype=float), 2).tolist()


def run_site(site, dem, ets):
    lat, lon = site["lat"], site["lon"]
    hz_az, hz_el = horizon(dem, lat, lon, obs_height=OBS_HEIGHT, n_az=N_AZ)
    s_az, s_el, s_d = eph.az_el("SUN", ets, lat, lon)
    e_az, e_el, _ = eph.az_el("EARTH", ets, lat, lon)
    frac = sun_fraction(s_el, s_az, s_d, hz_az, hz_el)
    vis = earth_visible(e_el, e_az, hz_az, hz_el)
    return {
        **site,
        "ground_height_m": round(float(sample(dem, np.array([lat]), np.array([lon]))[0]), 1),
        "observer_height_m": OBS_HEIGHT,
        "horizon": {"az_step_deg": 360 / N_AZ, "el_deg": r2(hz_el)},
        "time": {"start_utc": sp.et2utc(ets[0], "ISOC", 0) + "Z", "step_s": STEP_S, "n": len(ets)},
        "sun": {"az": r2(s_az), "el": r2(s_el), "frac": r2(frac)},
        "earth": {"az": r2(e_az), "el": r2(e_el), "visible": vis.astype(int).tolist()},
        "summary": summarize(frac, vis, STEP_S / 3600),
    }


def main(ids):
    sites = json.loads((Path(__file__).parent / "sites.json").read_text())
    if ids:
        sites = [s for s in sites if s["id"] in ids]
    eph.load_kernels()
    ets = eph.times(START, END, STEP_S)
    dem = load_lola_polar(DEM_PATH)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index = []
    for site in sites:
        data = run_site(site, dem, ets)
        (OUT_DIR / f"{site['id']}.json").write_text(json.dumps(data, separators=(",", ":")))
        index.append({k: data[k] for k in ("id", "name", "lat", "lon", "source", "summary")})
        print(site["id"], data["summary"])
    if not ids:
        meta = {
            "window_utc": [START, END], "step_s": STEP_S, "observer_height_m": OBS_HEIGHT,
            "dem": "LOLA LDEM_75S_120M (PDS), 120 m/px polar stereographic",
            "kernels": eph.KERNELS,
            "notes": "No refraction (airless). Sun as uniform disk; Earth visible when its center is above the horizon.",
        }
        (OUT_DIR / "sites.json").write_text(json.dumps({"meta": meta, "sites": index}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
