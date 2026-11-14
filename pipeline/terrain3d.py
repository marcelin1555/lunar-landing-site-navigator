"""Low-res terrain for the 3D picker: heights (LOLA 120 m, block mean) and PGDA mean solar visibility, 512 x 512.

Usage: python terrain3d.py   (needs data/raw/AVGVISIB_75S_120M_201608.TIF)
"""
import json

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window

from export import DEM_PATH, OUT_DIR
from horizon import load_lola_polar

N, FACTOR = 512, 10  # 512 px * 10 * 120 m = 614 km square around the pole
ILLUM = DEM_PATH.parent / "AVGVISIB_75S_120M_201608.TIF"  # from https://pgda.gsfc.nasa.gov/data/MoonIllumination/


def main():
    dem = load_lola_polar(DEM_PATH)
    crop = N * FACTOR
    o = (dem.z.shape[0] - crop) // 2
    z = dem.z[o:o + crop, o:o + crop].reshape(N, FACTOR, N, FACTOR).mean(axis=(1, 3))
    with rasterio.open(ILLUM) as m:
        ill = m.read(1, window=Window(o, o, crop, crop), out_shape=(N, N), resampling=Resampling.average)
    ill = np.clip(ill * 4e-5, 0, 1)  # DN scaling from the PDS label
    out = OUT_DIR / "free"
    np.round(z).astype("<i2").tofile(out / "terrain_512.i16")
    np.round(ill * 255).astype("u1").tofile(out / "illum_512.u8")
    res = dem.res * FACTOR
    half = N * res / 2
    meta = {"n": N, "res": res, "x0": -half + res / 2, "y0": half - res / 2}
    (out / "terrain.json").write_text(json.dumps(meta))
    print(meta, "height range", z.min(), z.max())


if __name__ == "__main__":
    main()
