export type Summary = {
  sunlit_pct: number;
  earth_visible_pct: number;
  sun_and_earth_pct: number;
  longest_dark_h: number;
  longest_no_earth_h: number;
};

export type SiteIndex = { id: string; name: string; lat: number; lon: number; source: string; summary: Summary };

export type Meta = {
  window_utc: [string, string];
  step_s: number;
  observer_height_m: number;
  dem: string;
  kernels: string[];
  notes: string;
};

export type Site = SiteIndex & {
  ground_height_m: number;
  observer_height_m: number;
  horizon: { az_step_deg: number; el_deg: number[] };
  time: { start_utc: string; step_s: number; n: number };
  sun: { az: number[]; el: number[]; frac: number[] };
  earth: { az: number[]; el: number[]; visible: number[] };
};

const base = import.meta.env.BASE_URL;

export async function loadIndex(): Promise<{ meta: Meta; sites: SiteIndex[] }> {
  const r = await fetch(`${base}data/sites.json`);
  if (!r.ok) throw new Error(`Could not load the site list (HTTP ${r.status}).`);
  return r.json();
}

const cache = new Map<string, Promise<Site>>();
export function loadSite(id: string): Promise<Site> {
  if (!cache.has(id)) {
    const p = fetch(`${base}data/${id}.json`).then((r) => {
      if (!r.ok) throw new Error(`Could not load data for ${id} (HTTP ${r.status}).`);
      return r.json() as Promise<Site>;
    });
    p.catch(() => cache.delete(id));
    cache.set(id, p);
  }
  return cache.get(id)!;
}

export const startMs = (s: Site) => Date.parse(s.time.start_utc);
export const timeAt = (s: Site, i: number) => new Date(startMs(s) + i * s.time.step_s * 1000);

/** Index of the hourly sample at or before date, or -1 when outside the computed window. */
export function indexAt(s: Site, date: Date): number {
  const i = Math.floor((date.getTime() - startMs(s)) / (s.time.step_s * 1000));
  return i >= 0 && i < s.time.n ? i : -1;
}

export const sunUp = (s: Site, i: number) => s.sun.frac[i] >= 0.5;
export const earthUp = (s: Site, i: number) => s.earth.visible[i] === 1;

/** Hours until the boolean state changes after index i, or null if it never changes inside the window. */
export function hoursUntilChange(s: Site, i: number, state: (s: Site, i: number) => boolean): number | null {
  const now = state(s, i);
  for (let j = i + 1; j < s.time.n; j++) if (state(s, j) !== now) return ((j - i) * s.time.step_s) / 3600;
  return null;
}

export function horizonAt(s: Site, az: number): number {
  const n = s.horizon.el_deg.length;
  const x = (((az % 360) + 360) % 360) / s.horizon.az_step_deg;
  const k = Math.floor(x) % n;
  const t = x - Math.floor(x);
  return s.horizon.el_deg[k] * (1 - t) + s.horizon.el_deg[(k + 1) % n] * t;
}

export function fmtDuration(h: number | null): string {
  if (h === null) return "beyond data window";
  const d = Math.floor(h / 24);
  const r = Math.round(h - d * 24);
  return d > 0 ? `${d} d ${r} h` : `${r} h`;
}

export const fmtDeg = (v: number) => `${v >= 0 ? "+" : "−"}${Math.abs(v).toFixed(2)}°`;
export const fmtLatLon = (lat: number, lon: number) =>
  `${Math.abs(lat).toFixed(3)}°${lat < 0 ? "S" : "N"} ${lon.toFixed(3)}°E`;
