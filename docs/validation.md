# Validation against PGDA average maps

PGDA averages cover 18.6 years (a full lunar nodal cycle); ours cover Nov 2026 to Dec 2028,
so a few percentage points of difference are expected. Run after export.py (needs network).


| Site | Sunlit, ours | Sunlit, PGDA | Δ | Earth, ours | Earth, PGDA | Δ |
|---|---:|---:|---:|---:|---:|---:|
| Connecting Ridge | 57.8% | 53.3% | +4.5 | 49.7% | 53.4% | -3.7 |
| Peak near Shackleton | 36.3% | 37.6% | -1.3 | 51.4% | 53.4% | -2.0 |
| Mons Mouton | 27.5% | 29.1% | -1.6 | 57.6% | 61.2% | -3.6 |
| Shackleton Rim | 87.3% | 89.6% | -2.3 | 49.8% | 53.8% | -4.0 |
| Nobile Rim 1 | 88.3% | 85.8% | +2.5 | 57.2% | 60.2% | -3.0 |
| de Gerlache Rim | 79.3% | 79.7% | -0.4 | 57.3% | 61.1% | -3.8 |
| Leibnitz Beta Plateau | 79.3% | 80.0% | -0.7 | 64.1% | 64.3% | -0.2 |
| Malapert Massif | 83.6% | 84.5% | -0.9 | 74.0% | 71.0% | +3.0 |
| Haworth | 75.3% | 75.2% | +0.1 | 62.5% | 68.3% | -5.8 |
| Nobile Rim 2 | 53.4% | 53.9% | -0.5 | 74.0% | 71.8% | +2.2 |

Mean absolute difference: sunlit 1.5 pts, Earth 3.1 pts.
