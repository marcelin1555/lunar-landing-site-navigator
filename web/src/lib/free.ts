// Compute any south-polar point in the browser: same math as pipeline/ (horizon.py, ephemeris.py,
// visibility.py, summarize.py), on a 240 m DEM and precomputed Sun/Earth vectors from SPICE.
import type { Site, Summary } from "./data";

export type FreeMeta = {
  n_times: number;
  start_utc: string;
  step_s: number;
  dem: { res: number; x0: number; y0: number; size: number; tiles: number; tile_size: number; dn_scale: number };
};
export type Tiles = Map<string, Int16Array>;

const R = 1737400; // m
const R_KM = 1737.4;
const SUN_RADIUS_KM = 696000;
export const N_AZ = 720;
export const MAX_DIST = 150e3;
const D2R = Math.PI / 180;

export function stereoSouth(lat: number, lon: number): [number, number] {
  const rho = 2 * R * Math.tan(Math.PI / 4 + (lat * D2R) / 2);
  return [rho * Math.sin(lon * D2R), rho * Math.cos(lon * D2R)];
}

export function fromStereo(x: number, y: number): [number, number] {
  const lat = (2 * Math.atan(Math.hypot(x, y) / (2 * R))) / D2R - 90;
  return [lat, ((Math.atan2(x, y) / D2R) % 360 + 360) % 360];
}

/** Tile keys "r_c" that cover every ray from (lat, lon). */
export function tilesFor(meta: FreeMeta, lat: number, lon: number): string[] {
  const [x, y] = stereoSouth(lat, lon);
  const d = meta.dem;
  const pad = MAX_DIST * 1.05 + 2 * d.res; // stereographic scale >= 1 near the pole, small margin
  const c0 = Math.floor((x - pad - d.x0) / d.res / d.tile_size), c1 = Math.floor((x + pad - d.x0) / d.res / d.tile_size);
  const r0 = Math.floor((d.y0 - (y + pad)) / d.res / d.tile_size), r1 = Math.floor((d.y0 - (y - pad)) / d.res / d.tile_size);
  const keys: string[] = [];
  for (let r = Math.max(0, r0); r <= Math.min(d.tiles - 1, r1); r++)
    for (let c = Math.max(0, c0); c <= Math.min(d.tiles - 1, c1); c++) keys.push(`${r}_${c}`);
  return keys;
}

function makeSampler(meta: FreeMeta, tiles: Tiles) {
  const d = meta.dem, ts = d.tile_size;
  const at = (row: number, col: number) => {
    if (row < 0 || col < 0 || row >= d.size || col >= d.size) return NaN;
    const t = tiles.get(`${Math.floor(row / ts)}_${Math.floor(col / ts)}`);
    return t ? t[(row % ts) * ts + (col % ts)] * d.dn_scale : NaN;
  };
  return (lat: number, lon: number) => {
    const [x, y] = stereoSouth(lat, lon);
    const fr = (d.y0 - y) / d.res, fc = (x - d.x0) / d.res;
    const r = Math.floor(fr), c = Math.floor(fc), tr = fr - r, tc = fc - c;
    return (at(r, c) * (1 - tc) + at(r, c + 1) * tc) * (1 - tr) + (at(r + 1, c) * (1 - tc) + at(r + 1, c + 1) * tc) * tr;
  };
}

const unit = (lat: number, lon: number): [number, number, number] => {
  const la = lat * D2R, lo = lon * D2R;
  return [Math.cos(la) * Math.cos(lo), Math.cos(la) * Math.sin(lo), Math.sin(la)];
};

export function horizon(meta: FreeMeta, tiles: Tiles, lat: number, lon: number, obsHeight = 2) {
  const sample = makeSampler(meta, tiles);
  const step = meta.dem.res;
  const h0 = sample(lat, lon);
  const up = unit(lat, lon);
  const p0 = up.map((u) => (R + h0 + obsHeight) * u);
  const p1 = lat * D2R, l1 = lon * D2R;
  const el = new Array<number>(N_AZ);
  for (let k = 0; k < N_AZ; k++) {
    const a = ((k * 360) / N_AZ) * D2R;
    let best = -Infinity;
    for (let dist = step; dist <= MAX_DIST + 1e-6; dist += step) {
      const s = dist / R;
      const p2 = Math.asin(Math.sin(p1) * Math.cos(s) + Math.cos(p1) * Math.sin(s) * Math.cos(a));
      const l2 = l1 + Math.atan2(Math.sin(a) * Math.sin(s) * Math.cos(p1), Math.cos(s) - Math.sin(p1) * Math.sin(p2));
      const h = sample(p2 / D2R, l2 / D2R);
      if (Number.isNaN(h)) break; // ray left the DEM
      const u = unit(p2 / D2R, l2 / D2R);
      const v = [(R + h) * u[0] - p0[0], (R + h) * u[1] - p0[1], (R + h) * u[2] - p0[2]];
      const e = Math.asin((v[0] * up[0] + v[1] * up[1] + v[2] * up[2]) / Math.hypot(v[0], v[1], v[2]));
      if (e > best) best = e;
    }
    el[k] = best / D2R;
  }
  return { el, groundHeight: h0 };
}

function horizonAt(el: number[], az: number) {
  const x = (((az % 360) + 360) % 360) / (360 / N_AZ);
  const k = Math.floor(x) % N_AZ, t = x - Math.floor(x);
  return el[k] * (1 - t) + el[(k + 1) % N_AZ] * t;
}

function longestRun(mask: boolean[]) {
  let best = 0, run = 0;
  for (const m of mask) { run = m ? run + 1 : 0; if (run > best) best = run; }
  return best;
}

const r1 = (v: number) => Math.round(v * 10) / 10;
const r2 = (v: number) => Math.round(v * 100) / 100;

export function computeSite(meta: FreeMeta, sky: Float32Array, tiles: Tiles, lat: number, lon: number, id: string, name: string): Site {
  const hz = horizon(meta, tiles, lat, lon);
  const up = unit(lat, lon);
  const east = [-Math.sin(lon * D2R), Math.cos(lon * D2R), 0];
  const north = [up[1] * east[2] - up[2] * east[1], up[2] * east[0] - up[0] * east[2], up[0] * east[1] - up[1] * east[0]];
  const n = meta.n_times;
  const sun = { az: new Array<number>(n), el: new Array<number>(n), frac: new Array<number>(n) };
  const earth = { az: new Array<number>(n), el: new Array<number>(n), visible: new Array<number>(n) };
  const azEl = (o: number): [number, number, number] => {
    const v = [sky[o] - R_KM * up[0], sky[o + 1] - R_KM * up[1], sky[o + 2] - R_KM * up[2]];
    const dist = Math.hypot(v[0], v[1], v[2]);
    const e = v[0] * east[0] + v[1] * east[1];
    const nn = v[0] * north[0] + v[1] * north[1] + v[2] * north[2];
    const u = v[0] * up[0] + v[1] * up[1] + v[2] * up[2];
    return [((Math.atan2(e, nn) / D2R) % 360 + 360) % 360, Math.asin(u / dist) / D2R, dist];
  };
  let fracSum = 0, earthSum = 0, both = 0;
  const lit: boolean[] = new Array(n), seen: boolean[] = new Array(n);
  for (let i = 0; i < n; i++) {
    const [saz, sel, sd] = azEl(i * 6);
    const r = Math.asin(SUN_RADIUS_KM / sd) / D2R;
    const t = Math.min(1, Math.max(-1, (sel - horizonAt(hz.el, saz)) / r));
    const frac = 1 - (Math.acos(t) - t * Math.sqrt(1 - t * t)) / Math.PI;
    const [eaz, eel] = azEl(i * 6 + 3);
    const vis = eel > horizonAt(hz.el, eaz);
    sun.az[i] = r2(saz); sun.el[i] = r2(sel); sun.frac[i] = r2(frac);
    earth.az[i] = r2(eaz); earth.el[i] = r2(eel); earth.visible[i] = vis ? 1 : 0;
    fracSum += frac; earthSum += +vis;
    lit[i] = frac >= 0.5; seen[i] = vis;
    if (lit[i] && vis) both++;
  }
  const hours = meta.step_s / 3600;
  const summary: Summary = {
    sunlit_pct: r1((fracSum / n) * 100),
    earth_visible_pct: r1((earthSum / n) * 100),
    sun_and_earth_pct: r1((both / n) * 100),
    longest_dark_h: r1(longestRun(lit.map((v) => !v)) * hours),
    longest_no_earth_h: r1(longestRun(seen.map((v) => !v)) * hours),
  };
  return {
    id, name, lat: Math.round(lat * 1e5) / 1e5, lon: Math.round(lon * 1e5) / 1e5,
    source: `Custom point, computed in the browser on a ${meta.dem.res} m DEM`,
    summary, ground_height_m: r1(hz.groundHeight), observer_height_m: 2,
    horizon: { az_step_deg: 360 / N_AZ, el_deg: hz.el.map(r2) },
    time: { start_utc: meta.start_utc, step_s: meta.step_s, n },
    sun, earth,
  };
}
