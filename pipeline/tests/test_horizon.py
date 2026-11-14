import numpy as np

from horizon import R_MOON, Dem, destination, horizon, stereo_south


def flat_dem(res=120.0, half=1500):
    n = 2 * half + 1
    return Dem(z=np.zeros((n, n), dtype=np.float32), x0=-half * res, y0=half * res, res=res)


def test_flat_sphere_gives_geometric_dip():
    dem = flat_dem()
    h = 2.0
    _, el = horizon(dem, -89.5, 45.0, obs_height=h, n_az=36, max_dist=20e3, step=10.0)
    dip = -np.degrees(np.arccos(R_MOON / (R_MOON + h)))
    assert np.allclose(el, dip, atol=0.002)


def test_wall_matches_angle_with_curvature():
    dem = flat_dem()
    lat, lon, H, D = -89.0, 0.0, 500.0, 10e3
    # raise a wall ring at distance D around the site
    ys, xs = np.mgrid[0:dem.z.shape[0], 0:dem.z.shape[1]]
    x, y = dem.x0 + xs * dem.res, dem.y0 - ys * dem.res
    sx, sy = stereo_south(lat, lon)
    r = np.hypot(x - sx, y - sy)
    dem.z[(r > D) & (r < D + 2 * dem.res)] = H
    _, el = horizon(dem, lat, lon, obs_height=0.0, n_az=36, max_dist=15e3, step=20.0)
    def exact(dist):  # elevation of a point H high at arc distance dist, observer on the sphere
        s = dist / R_MOON
        return np.degrees(np.arctan2((R_MOON + H) * np.cos(s) - R_MOON, (R_MOON + H) * np.sin(s)))

    # the rasterized ring has full height only between D and D + 2 px; curvature alone is ~0.16 deg here
    assert np.all(el <= exact(D) + 0.01)
    assert np.all(el >= exact(D + 2 * dem.res) - 0.04)


def test_destination_roundtrip_north():
    lat, lon = destination(-89.0, 0.0, 0.0, np.radians(1.0) * R_MOON)
    assert np.isclose(lat, -88.0)
