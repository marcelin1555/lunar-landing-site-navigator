// Checks the browser computation (free.ts, 240 m DEM) against the pipeline output (120 m DEM).
// Run: node --experimental-strip-types scripts/validate-free.ts
import { readFileSync } from "node:fs";
import { computeSite, tilesFor, type FreeMeta, type Tiles } from "../src/lib/free.ts";

const dir = new URL("../public/data/", import.meta.url);
const meta: FreeMeta = JSON.parse(readFileSync(new URL("free/meta.json", dir), "utf8"));
const buf = (p: string) => { const b = readFileSync(new URL(p, dir)); return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength); };
const sky = new Float32Array(buf("free/sky.f32"));
const index = JSON.parse(readFileSync(new URL("sites.json", dir), "utf8"));

let worst = 0;
const diffs: number[] = [];
for (const s of index.sites) {
  const tiles: Tiles = new Map(tilesFor(meta, s.lat, s.lon).map((k) => [k, new Int16Array(buf(`free/dem_${k}.i16`))]));
  const t0 = performance.now();
  const c = computeSite(meta, sky, tiles, s.lat, s.lon, s.id, s.name);
  const ms = performance.now() - t0;
  const ref = JSON.parse(readFileSync(new URL(`${s.id}.json`, dir), "utf8"));
  // the Sun/Earth path must match the pipeline exactly (same SPICE vectors)
  for (let i = 0; i < ref.sun.el.length; i += 97) {
    worst = Math.max(worst, Math.abs(c.sun.el[i] - ref.sun.el[i]), Math.abs(c.earth.el[i] - ref.earth.el[i]));
  }
  const d = c.summary.sunlit_pct - ref.summary.sunlit_pct;
  diffs.push(Math.abs(d));
  console.log(`${s.id.padEnd(22)} sunlit ${c.summary.sunlit_pct} vs ${ref.summary.sunlit_pct} (${d >= 0 ? "+" : ""}${d.toFixed(1)})  earth ${c.summary.earth_visible_pct} vs ${ref.summary.earth_visible_pct}  ${ms.toFixed(0)} ms, ${tiles.size} tiles`);
}
const mean = diffs.reduce((a, b) => a + b, 0) / diffs.length;
console.log(`max Sun/Earth elevation difference ${worst.toFixed(3)} deg; mean |sunlit diff| ${mean.toFixed(1)} pts`);
if (worst > 0.02 || mean > 3) process.exit(1);
