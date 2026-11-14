import numpy as np
import pytest

import ephemeris as eph
from visibility import earth_visible, sun_fraction

pytestmark = pytest.mark.skipif(not (eph.KERNEL_DIR / "de440s.bsp").exists(), reason="kernels not downloaded")


@pytest.fixture(scope="module", autouse=True)
def kernels():
    eph.load_kernels()


def test_sun_stays_near_horizon_at_pole():
    ets = eph.times("2027-01-01", "2027-12-31", 6 * 3600)
    _, el, dist = eph.az_el("SUN", ets, -89.9, 0.0)
    assert np.abs(el).max() < 1.75  # lunar obliquity to the ecliptic is 1.54 deg
    assert np.allclose(dist, 1.496e8, rtol=0.03)


def test_earth_librates_around_horizon_at_pole():
    ets = eph.times("2027-01-01", "2027-03-01", 3600)
    _, el, dist = eph.az_el("EARTH", ets, -89.9, 0.0)
    assert 4 < el.max() < 8 and -8 < el.min() < -4  # libration in latitude ~6.7 deg
    assert 3.5e5 < dist.min() and dist.max() < 4.1e5


def test_sun_fraction_limits():
    hz_az, hz_el = np.array([0.0, 180.0]), np.array([0.0, 0.0])
    dist = np.full(3, 1.496e8)
    f = sun_fraction(np.array([1.0, 0.0, -1.0]), np.zeros(3), dist, hz_az, hz_el)
    assert np.allclose(f, [1.0, 0.5, 0.0])
    assert earth_visible(np.array([0.1]), np.array([90.0]), hz_az, hz_el)[0]


def test_matches_jpl_horizons_connecting_ridge():
    # JPL Horizons API, observer coord@301 geodetic 209.94767E -89.53432 h=0, QUANTITIES=4, fetched 2026-11-14
    ets = eph.times("2027-01-01", "2027-01-03", 43200)
    sun = [(53.175511, 1.293050), (47.092309, 1.322902), (41.007455, 1.349438), (34.921039, 1.372213), (28.833162, 1.390821)]
    earth = [(157.218271, -6.677410), (156.931727, -6.974515), (156.582622, -7.193826), (156.177789, -7.335229), (155.723660, -7.399210)]
    for body, ref in (("SUN", sun), ("EARTH", earth)):
        az, el, _ = eph.az_el(body, ets, -89.53432, 209.94767)
        assert np.allclose(az, [r[0] for r in ref], atol=0.01)
        assert np.allclose(el, [r[1] for r in ref], atol=0.005)
