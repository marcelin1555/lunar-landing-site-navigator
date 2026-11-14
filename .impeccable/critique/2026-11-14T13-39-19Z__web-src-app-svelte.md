---
target: web app (App.svelte)
total_score: 26
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 4
target_identity: "file:F:\\HACKATHON CG\\lunar-navigator\\web\\src\\App.svelte"
target_fingerprint: "sha256:c75051d776a72cb4c6099ef1d3b1a25a4b47f10736508652f0778ff5e976633e"
target_path: "F:\\HACKATHON CG\\lunar-navigator\\web\\src\\App.svelte"
timestamp: 2026-11-14T13-39-19Z
slug: web-src-app-svelte
---
Method: dual-agent (A: design review subagent · B: detector + browser subagent)

## Design Health Score
| # | Heuristic | Score | Key Issue |
|---|---|---|---|
| 1 | Visibility of System Status | 3 | No loading state while terrain tiles stream or a custom point computes (only a small map HUD line) |
| 2 | Match System / Real World | 2 | "Up" shown with "elevation −0.60°" (Malapert summit); physically right, reads as a bug |
| 3 | User Control and Freedom | 3 | Releasing a drag on terrain creates a point with no confirm/undo |
| 4 | Consistency and Standards | 2 | Duration formats "74h"/"3 d 2 h"/"29 d 22 h"; Sun orange reused for best-Earth, Play, focus; site name twice |
| 5 | Error Prevention | 3 | Accidental terrain clicks unguarded |
| 6 | Recognition Rather Than Recall | 2 | Map pins unlabeled except selected |
| 7 | Flexibility and Efficiency | 3 | Deep links, sort, compare; no global shortcuts (Space, arrows) |
| 8 | Aesthetic and Minimalist Design | 3 | 11px text over terrain; KPI strip of 5 equal-weight numbers |
| 9 | Error Recovery | 2 | Permanent-shadow point reads "beyond data window", zeros, empty bars |
| 10 | Help and Documentation | 3 | Strong method footer; "Both"/"Max dark" unexplained |
| **Total** | | **26/40** | **Acceptable** |

## Design Specificity Verdict
LLM: above the fold is authored (real-light curved LOLA terrain, instrument panel, skyline with Sun/Earth paths, mission copy). Below the fold reverts to generic table/KPI strip/form. Weakest link: anonymous pins on the hero.
Deterministic: CLI 0 findings. Live overlay 14-15 per view: tiny-text 11px (Map3D.svelte:258, App.svelte:163,192,198,205), undersized-ui-text 10px "custom" tag (SiteTable.svelte:56), straggler (App.svelte:224). False positives: custom-tag count depends on localStorage; straggler only at narrow widths. Contrast: text-dim 6.4:1 on bg; HUD hint over terrain down to 1.6:1. Mobile 375px: Compare table (Compare.svelte:38) forces page scrollWidth 475. 38 controls under 24px.

## Priority Issues
- [P1] Unlabeled map pins. Fix: always-on muted labels, table-row hover highlights pin. /impeccable clarify
- [P1] No "which site is best" verdict. Fix: one-line verdict per mission profile. /impeccable clarify
- [P1] Contradictory/empty states (negative elevation "Up", permanent shadow as zeros, "never lit" in hours column). Fix: lead with over-terrain value; dedicated permanently-shadowed state. /impeccable harden
- [P1] Compare table overflows mobile; tap targets <24px. /impeccable adapt
- [P2] Sun orange overloaded (best values, Play, focus). /impeccable colorize

## Persona Red Flags
Alex: no jump-by-name on map, no global shortcuts, fixed Play speed, accidental point creation.
Sam: map has no keyboard path, skyline not exposed as text, datetime shows local format labeled UTC.
NASA judge: strong at 5 s; at 20 s unlabeled pins, negative "Up", no verdict; Horizons validation buried in footer.

## Minor Observations
h1 18px smaller than 24px h2s; PGDA mode toggle nearly invisible; HUD hint 11px low contrast; machine names for custom points, no rename; "Both" vs "Sun and Earth" naming; five time frames without per-block horizon tags.

## Questions to Consider
1. Draw the Sun/Earth bearing on the map itself?
2. Commit to a recommendation per mission profile?
3. Celebrate "never lit" (where the ice is)?
