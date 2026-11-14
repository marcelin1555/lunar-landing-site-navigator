"""Named south-polar features from the IAU Gazetteer of Planetary Nomenclature (USGS) -> web/public/data/features.json.

Usage: python features.py path/to/MOON_nomenclature_center_pts.dbf
Source: https://planetarynames.wr.usgs.gov/shapefiles/MOON_nomenclature_center_pts.zip
"""
import json
import struct
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "web" / "public" / "data" / "features.json"
LAT_LIMIT = -80.5  # same limit as custom points in the browser


def read_dbf(path):
    data = Path(path).read_bytes()
    n, header_len, rec_len = struct.unpack("<IHH", data[4:12])
    fields, pos = [], 32
    while data[pos] != 0x0D:
        name = data[pos:pos + 11].split(b"\0")[0].decode()
        fields.append((name, data[pos + 16]))
        pos += 32
    for i in range(n):
        rec = data[header_len + i * rec_len: header_len + (i + 1) * rec_len]
        if rec[:1] == b"*":  # deleted record
            continue
        row, off = {}, 1
        for name, length in fields:
            row[name] = rec[off:off + length].decode("utf-8", "replace").strip()
            off += length
        yield row


def main(dbf):
    out = []
    for r in read_dbf(dbf):
        lat, lon = float(r["center_lat"]), float(r["center_lon"]) % 360
        if lat <= LAT_LIMIT and r.get("approval", "").startswith("Adopted"):
            out.append({"name": r["clean_name"], "type": r["type"].split(",")[0], "lat": round(lat, 4), "lon": round(lon, 4),
                        "diameter_km": round(float(r["diameter"] or 0), 1)})
    out.sort(key=lambda f: f["name"])
    OUT.write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(len(out), "features;", ", ".join(f["name"] for f in out[:30]))


if __name__ == "__main__":
    main(sys.argv[1])
