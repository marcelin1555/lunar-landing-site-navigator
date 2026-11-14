// Quick check of a named feature: node --experimental-strip-types scripts/check-feature.ts Shackleton
import { readFileSync } from "node:fs";
import { computeSite, tilesFor, type Tiles } from "../src/lib/free.ts";
const dir = new URL("../public/data/", import.meta.url);
const buf = (p: string) => { const b = readFileSync(new URL(p, dir)); return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength); };
const meta = JSON.parse(readFileSync(new URL("free/meta.json", dir), "utf8"));
const sky = new Float32Array(buf("free/sky.f32"));
const f = JSON.parse(readFileSync(new URL("features.json", dir), "utf8")).find((x: any) => x.name === process.argv[2]);
const tiles: Tiles = new Map(tilesFor(meta, f.lat, f.lon).map((k) => [k, new Int16Array(buf(`free/dem_${k}.i16`))]));
console.log(f, computeSite(meta, sky, tiles, f.lat, f.lon, "x", f.name).summary);
