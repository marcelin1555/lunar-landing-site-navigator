---
target: web/src/App.svelte
total_score: 26
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 2
target_identity: "file:F:\\HACKATHON CG\\lunar-navigator\\web\\src\\App.svelte"
target_fingerprint: "sha256:c3f40b1a2b5f245abb83f643a68ab797ed1148f46c80b495e81b82c19abcfa6e"
target_path: "F:\\HACKATHON CG\\lunar-navigator\\web\\src\\App.svelte"
timestamp: 2026-11-14T13-54-50Z
slug: web-src-app-svelte
---
Method: dual-agent (A: design review · B: detector + browser)

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Live Sun/Earth state with countdowns; Play has no rate shown; custom point "Computing…" has no progress |
| 2 | Match System / Real World | 3 | "−17.96° over terrain" wording; "Haworth" candidate vs "Haworth" PSR crater |
| 3 | User Control and Freedom | 3 | No undo for removed custom point; single map click commits a point |
| 4 | Consistency and Standards | 2 | Earth blue has 5 meanings; "best" has 3 styles; table = 2 years, Compare = 30 days |
| 5 | Error Prevention | 2 | Compare limit silently disables checkboxes |
| 6 | Recognition Rather Than Recall | 2 | 6 of 11 pins unlabeled at default camera (incl. verdict winners); column meanings only in title |
| 7 | Flexibility and Efficiency | 3 | Deep links, sort, feature search; no global shortcuts for time/Play |
| 8 | Aesthetic and Minimalist Design | 2 | Dense instrument panel; detail column flat, all same weight |
| 9 | Error Recovery | 3 | role=alert validation, WebGL fallback, out-of-window state |
| 10 | Help and Documentation | 3 | Method footer, validation badge; no inline explanation of PSR / vs flat horizon |
| **Total** | | **26/40** | **Acceptable** |

## Design Specificity Verdict
LLM: authored for this product (real Sun-lit map, rise/set countdowns, over-terrain vs flat horizon, skyline, PSR ice copy, mission-need verdict). Visual layer below the map is generic dark dev-tool.
Deterministic scan: 0 findings (exit 0) across web/src. Live overlay not run: browser pane blocked localhost detect.js (ERR_BLOCKED_BY_CLIENT). Mobile 375: no page overflow; only sub-24px targets are 18px checkboxes inside 28px label.hit (false positive).

## Priority Issues
- [P1] Half the map pins still unnamed (collision culling drops Nobile Rim 1, Shackleton Rim). Fix: always label verdict winners/compared/selected; numbered pins keyed to table; custom pins distinct shape. Command: layout, clarify.
- [P1] Compare sits inside the selected site's record and uses an unstated 30-day frame; all-tie "0h" rows all underlined as best. Fix: own section, state the frame, no "best" on ties, "none" instead of 0h. Command: layout, clarify.
- [P2] Earth blue overloaded (custom points, custom tag, PSR headline, best-Earth). Command: colorize.
- [P2] App opens on Connecting Ridge (index order), not the verdict winner; flat below-fold hierarchy. Command: bolder / distill.
- [P2] Mobile: compare hides 3rd site, site table hides Night max, timeline ticks collide. Command: adapt.

## Persona Red Flags
- Alex: no shortcuts for ±1h/±1d/Play; fixed Play rate; one-direction sort; no export.
- Sam: 3D map has no keyboard path (table alternative unstated); disabled checkboxes give no reason; no aria-current on selected row; no live region during Play.
- Mission planner: no trade-off/constraint view (night ≤ X days, Earth ≥ Y%); Haworth naming collision; no landing-window view.

## Minor Observations
- "Night max" / "Longest night" / "Shortest night": three names for one metric.
- "Map lit by the Sun… over 68°E, +1.55° at the pole" is expert noise in the primary panel.
- Mean sunlight toggle has no legend.
- datetime-local shows local date format next to "UTC".

## Questions to Consider
- Why does the app open on a site it does not recommend?
- Is the 3D map a decision tool or a hero image? Should the skyline move up?
- Should the verdict be driven by a user battery spec and comms requirement?
