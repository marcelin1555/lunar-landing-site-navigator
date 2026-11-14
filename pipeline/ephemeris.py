"""Sun and Earth azimuth/elevation seen from a lunar surface site (SPICE)."""
from pathlib import Path

import numpy as np
import spiceypy as sp

KERNEL_DIR = Path(__file__).resolve().parent.parent / "data" / "kernels"
KERNELS = ["naif0012.tls", "pck00011.tpc", "de440s.bsp", "moon_pa_de440_200625.bpc", "moon_de440_250416.tf"]
R_MOON_KM = 1737.4


def load_kernels(kdir=KERNEL_DIR):
    for k in KERNELS:
        sp.furnsh(str(kdir / k))


def times(start_utc, end_utc, step_s=3600):
    et0, et1 = sp.str2et(start_utc), sp.str2et(end_utc)
    return np.arange(et0, et1 + 1, step_s)


def enu_basis(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    up = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    east = np.array([-np.sin(lo), np.cos(lo), 0.0])
    return east, np.cross(up, east), up


def az_el(body, ets, lat, lon, height_m=0.0, frame="MOON_ME"):
    """Azimuth (deg from north, clockwise), elevation (deg) and distance (km) of body at each ET."""
    pos, _ = sp.spkpos(body, list(ets), frame, "LT+S", "MOON")
    east, north, up = enu_basis(lat, lon)
    v = np.asarray(pos) - (R_MOON_KM + height_m / 1000.0) * up
    dist = np.linalg.norm(v, axis=1)
    az = np.degrees(np.arctan2(v @ east, v @ north)) % 360.0
    el = np.degrees(np.arcsin(v @ up / dist))
    return az, el, dist
