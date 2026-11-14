"""Per-site summary numbers from hourly visibility series."""
import numpy as np


def longest_run(mask):
    """Length of the longest run of True values."""
    m = np.concatenate([[0], np.asarray(mask, dtype=np.int8), [0]])
    edges = np.flatnonzero(np.diff(m))
    return int((edges[1::2] - edges[::2]).max()) if edges.size else 0


def summarize(sun_frac, earth_vis, step_h=1.0):
    lit = sun_frac >= 0.5
    return {
        "sunlit_pct": round(float(sun_frac.mean() * 100), 1),
        "earth_visible_pct": round(float(earth_vis.mean() * 100), 1),
        "sun_and_earth_pct": round(float((lit & earth_vis).mean() * 100), 1),
        "longest_dark_h": round(longest_run(~lit) * step_h, 1),
        "longest_no_earth_h": round(longest_run(~earth_vis) * step_h, 1),
    }
