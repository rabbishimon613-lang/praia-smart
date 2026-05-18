"""Pull Sentinel-2 thumbnails per beach from Microsoft Planetary Computer.

Keyless, free. Generates web/satellite/{beach_id}/{date_label}.png for
target offsets (hoje, -3d, -7d, -14d, -30d). Picks the nearest Sentinel-2
pass within ±5 days that has <30% cloud cover.
"""
import csv
import json
import os
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTOS = os.path.join(ROOT, "postos.csv")
OUTDIR = os.path.join(ROOT, "web", "satellite")
META_OUT = os.path.join(ROOT, "data", "satellite.json")

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
PREVIEW = "https://planetarycomputer.microsoft.com/api/data/v1/item/bbox"
COLOR_FORMULA = "Gamma RGB 3.5 Saturation 1.5 Sigmoidal RGB 15 0.35"

BBOX_HALF = 0.05            # ~5.5km each direction → 11km square
CLOUD_MAX = 30
SEARCH_WINDOW_DAYS = 10     # accept tile within ±10 days of target
TARGET_OFFSETS = [
    ("hoje", 0),
    ("3d", 3),
    ("7d", 7),
    ("14d", 14),
    ("30d", 30),
]


def curl_json(url, body=None):
    cmd = ["curl", "-sSfL", "-H", "Content-Type: application/json"]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    cmd.append(url)
    return json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)


def stac_search(lat, lng, target_date, window_days=SEARCH_WINDOW_DAYS):
    """Find the Sentinel-2 tile closest to target_date within window."""
    start = (target_date - timedelta(days=window_days)).strftime("%Y-%m-%d")
    end = (target_date + timedelta(days=window_days)).strftime("%Y-%m-%d")
    body = {
        "collections": ["sentinel-2-l2a"],
        "intersects": {"type": "Point", "coordinates": [lng, lat]},
        "datetime": f"{start}/{end}",
        "limit": 10,
        "sortby": [{"field": "properties.datetime", "direction": "desc"}],
        "query": {"eo:cloud_cover": {"lt": CLOUD_MAX}},
    }
    data = curl_json(STAC, body)
    features = data.get("features", [])
    if not features:
        return None
    # Pick the one whose date is closest to target_date
    def dist(f):
        dt = datetime.fromisoformat(f["properties"]["datetime"].replace("Z", "+00:00")).date()
        return abs((dt - target_date).days)
    features.sort(key=dist)
    f = features[0]
    return {
        "id": f["id"],
        "datetime": f["properties"]["datetime"][:10],
        "cloud": round(f["properties"].get("eo:cloud_cover", 0), 1),
    }


def fetch_crop(item_id, bbox, out_path, size=512):
    """Download a bbox crop PNG for the given item."""
    qs = urllib.parse.urlencode({
        "collection": "sentinel-2-l2a",
        "item": item_id,
        "assets": "B04",  # will pass multiple times
        "color_formula": COLOR_FORMULA,
        "width": size,
        "height": size,
    })
    # urlencode collapses dup keys; build assets manually
    url = (
        f"{PREVIEW}/{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}.png?"
        f"collection=sentinel-2-l2a&item={item_id}"
        f"&assets=B04&assets=B03&assets=B02"
        f"&color_formula={urllib.parse.quote(COLOR_FORMULA)}"
        f"&width={size}&height={size}"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    r = subprocess.run(
        ["curl", "-sSfL", "-o", out_path, "-w", "%{size_download}", url],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"curl failed for {item_id}: {r.stderr}")
    return int(r.stdout) if r.stdout else 0


def process_beach(beach):
    lat, lng = float(beach["lat"]), float(beach["lng"])
    bbox = [lng - BBOX_HALF, lat - BBOX_HALF, lng + BBOX_HALF, lat + BBOX_HALF]
    today = datetime.utcnow().date()
    records = []
    seen_items = set()  # avoid duplicate downloads for same tile

    for label, days_ago in TARGET_OFFSETS:
        target = today - timedelta(days=days_ago)
        tile = stac_search(lat, lng, target)
        if not tile:
            records.append({"label": label, "target": str(target), "status": "no_data"})
            print(f"    [{label:5}] no clear tile within ±{SEARCH_WINDOW_DAYS}d of {target}", file=sys.stderr)
            continue

        # Dedupe: if same tile already downloaded for this beach, just reference it
        if tile["id"] in seen_items:
            existing = next(r for r in records if r.get("item") == tile["id"])
            records.append({
                "label": label, "target": str(target), "status": "ok",
                "image": existing["image"], "date": tile["datetime"],
                "cloud": tile["cloud"], "item": tile["id"], "dedup": True,
            })
            continue

        out_path = os.path.join(OUTDIR, beach["id"], f"{label}.png")
        try:
            size = fetch_crop(tile["id"], bbox, out_path)
            print(f"    [{label:5}] {tile['datetime']} cloud={tile['cloud']:>4}% → {size//1024}KB", file=sys.stderr)
            records.append({
                "label": label, "target": str(target), "status": "ok",
                "date": tile["datetime"], "cloud": tile["cloud"],
                "item": tile["id"],
                "image": f"satellite/{beach['id']}/{label}.png",
            })
            seen_items.add(tile["id"])
        except Exception as e:
            print(f"    [{label:5}] ERR: {e}", file=sys.stderr)
            records.append({"label": label, "target": str(target), "status": "error"})

    return records


def main():
    beaches = list(csv.DictReader(open(POSTOS)))
    print(f"Fetching Sentinel-2 thumbnails for {len(beaches)} beaches × {len(TARGET_OFFSETS)} dates", file=sys.stderr)
    result = {}
    for b in beaches:
        print(f"  {b['id']}", file=sys.stderr)
        result[b["id"]] = process_beach(b)
    os.makedirs(os.path.dirname(META_OUT), exist_ok=True)
    json.dump({"fetched_at": int(time.time()), "by_beach": result},
              open(META_OUT, "w"), indent=2)
    print(f"\nWrote {META_OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
