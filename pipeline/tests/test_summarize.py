import numpy as np

from summarize import longest_run, summarize


def test_longest_run():
    assert longest_run([0, 1, 1, 0, 1, 1, 1, 0]) == 3
    assert longest_run([1, 1]) == 2
    assert longest_run([0, 0]) == 0


def test_summary_numbers():
    frac = np.array([1.0, 1.0, 0.0, 0.0, 0.0, 1.0])
    earth = np.array([True, False, False, True, True, True])
    s = summarize(frac, earth)
    assert s["sunlit_pct"] == 50.0
    assert s["longest_dark_h"] == 3
    assert s["sun_and_earth_pct"] == round(2 / 6 * 100, 1)
    assert s["longest_no_earth_h"] == 2
