"""Visibility of the Sun disk and the Earth above a local horizon profile."""
import numpy as np

SUN_RADIUS_KM = 696000.0


def horizon_at(hz_az, hz_el, az):
    return np.interp(az, hz_az, hz_el, period=360.0)


def sun_fraction(el, az, dist_km, hz_az, hz_el):
    """Fraction of the solar disk above the horizon (uniform disk, horizon locally straight)."""
    r = np.degrees(np.arcsin(SUN_RADIUS_KM / dist_km))
    t = np.clip((el - horizon_at(hz_az, hz_el, az)) / r, -1.0, 1.0)
    return 1.0 - (np.arccos(t) - t * np.sqrt(1.0 - t * t)) / np.pi


def earth_visible(el, az, hz_az, hz_el):
    """Earth center above the horizon."""
    return el > horizon_at(hz_az, hz_el, az)
