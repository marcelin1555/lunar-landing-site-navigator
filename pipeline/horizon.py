"""Local horizon profile from a LOLA polar stereographic DEM."""
from dataclasses import dataclass

import numpy as np
from scipy.ndimage import map_coordinates

R_MOON = 1737400.0  # m, LOLA reference sphere


@dataclass
class Dem:
    z: np.ndarray  # height above R_MOON (m), row 0 = top (max y)
    x0: float  # x of column 0 pixel center (m)
    y0: float  # y of row 0 pixel center (m)
    res: float  # pixel size (m)


def load_lola_polar(img_path, n=7624, res=120.0, offset_px=3811.5, scale=0.5):
    """LOLA PDS polar IMG (int16 LSB, height = DN * scale); defaults are from ldem_75s_120m.lbl."""
    z = np.fromfile(img_path, dtype="<i2").reshape(n, n).astype(np.float32) * scale
    return Dem(z=z, x0=-offset_px * res, y0=offset_px * res, res=res)


def unit(lat, lon):
    lat, lon = np.radians(lat), np.radians(lon)
    return np.stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)], axis=-1)


def stereo_south(lat, lon):
    """South polar stereographic on the sphere, true scale at the pole (LOLA PDS convention)."""
    rho = 2 * R_MOON * np.tan(np.pi / 4 + np.radians(lat) / 2)
    lon = np.radians(lon)
    return rho * np.sin(lon), rho * np.cos(lon)


def destination(lat, lon, az, d):
    """Great-circle point at distance d (m) and azimuth az (deg, from north, clockwise)."""
    p1, l1, a = np.radians(lat), np.radians(lon), np.radians(az)
    s = d / R_MOON
    p2 = np.arcsin(np.sin(p1) * np.cos(s) + np.cos(p1) * np.sin(s) * np.cos(a))
    l2 = l1 + np.arctan2(np.sin(a) * np.sin(s) * np.cos(p1), np.cos(s) - np.sin(p1) * np.sin(p2))
    return np.degrees(p2), np.degrees(l2)


def sample(dem, lat, lon):
    x, y = stereo_south(lat, lon)
    rows, cols = (dem.y0 - y) / dem.res, (x - dem.x0) / dem.res
    return map_coordinates(dem.z, [rows, cols], order=1, mode="constant", cval=np.nan)


def horizon(dem, lat, lon, obs_height=2.0, n_az=720, max_dist=150e3, step=None):
    """Return (azimuths deg, horizon elevation deg) seen from (lat, lon) at obs_height above ground."""
    step = step or dem.res
    az = np.arange(n_az) * 360.0 / n_az
    d = np.arange(step, max_dist + step, step)
    tlat, tlon = destination(lat, lon, az[:, None], d[None, :])
    h = sample(dem, tlat, tlon)
    h0 = float(sample(dem, np.array([lat]), np.array([lon]))[0])
    up = unit(lat, lon)
    p0 = (R_MOON + h0 + obs_height) * up
    v = (R_MOON + h)[..., None] * unit(tlat, tlon) - p0
    el = np.degrees(np.arcsin(v @ up / np.linalg.norm(v, axis=-1)))
    # shortcut: rays leaving the DEM are cut there (NaN); 75S grid reaches >1000 km from south-pole sites
    return az, np.nanmax(el, axis=1)
