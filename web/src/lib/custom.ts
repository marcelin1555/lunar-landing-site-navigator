import type { Site } from "./data";
import { computeSite, tilesFor, type FreeMeta, type Tiles } from "./free";

export type CustomPoint = { id: string; name: string; lat: number; lon: number };

const base = import.meta.env.BASE_URL;
const KEY = "lln.custom-points.v1";
export const LAT_LIMIT = -80.5; // rays need 150 km of DEM around the point (grid ends at 75°S)

let freeData: Promise<{ meta: FreeMeta; sky: Float32Array }> | null = null;
const tiles: Tiles = new Map();

async function buffer(path: string) {
  const r = await fetch(`${base}data/free/${path}`);
  if (!r.ok) throw new Error(`Could not download ${path} (HTTP ${r.status}).`);
  return r.arrayBuffer();
}

function loadFree() {
  freeData ??= Promise.all([
    fetch(`${base}data/free/meta.json`).then((r) => r.json() as Promise<FreeMeta>),
    buffer("sky.f32").then((b) => new Float32Array(b)),
  ]).then(([meta, sky]) => ({ meta, sky }));
  freeData.catch(() => (freeData = null));
  return freeData;
}

export async function computePoint(p: CustomPoint): Promise<Site> {
  const { meta, sky } = await loadFree();
  const missing = tilesFor(meta, p.lat, p.lon).filter((k) => !tiles.has(k));
  const loaded = await Promise.all(missing.map(async (k) => [k, new Int16Array(await buffer(`dem_${k}.i16`))] as const));
  for (const [k, t] of loaded) tiles.set(k, t);
  return computeSite(meta, sky, tiles, p.lat, p.lon, p.id, p.name);
}

export function validate(lat: number, lon: number): string | null {
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return "Enter latitude and longitude in decimal degrees.";
  if (lat > LAT_LIMIT || lat < -90) return `Latitude must be between −90° and ${LAT_LIMIT}° (south polar DEM coverage).`;
  return null;
}

export function loadSaved(): CustomPoint[] {
  try {
    const v = JSON.parse(localStorage.getItem(KEY) ?? "[]");
    return Array.isArray(v) ? v.filter((p) => validate(p.lat, p.lon) === null && typeof p.name === "string") : [];
  } catch {
    return [];
  }
}

export function save(points: CustomPoint[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(points));
  } catch {
    // storage blocked (private mode): points still work for this visit
  }
}

export const newId = () => `custom-${Date.now().toString(36)}`;
