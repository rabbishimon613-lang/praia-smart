"""Compute current + hourly 'movimento' estimate per beach.

v1: prior-only — deterministic formula based on:
  hour-of-day × day-of-week × weather (sun, temp, wind)

Writes data/agito.json. CV layer comes later and blends with this prior.
"""
import json
import math
import os
import sys
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONDITIONS = os.path.join(ROOT, "data", "conditions.json")
OUT = os.path.join(ROOT, "data", "agito.json")


def bell(x, center, width):
    return math.exp(-((x - center) ** 2) / (2 * width ** 2))


def score(hour, dow, temp_c, cloud_pct, wind_kmh, uv, precip_mm):
    """Return [0..1] movimento estimate. Tuned for Brazilian beaches."""
    # Night collapse — if UV is 0 we're outside daylight
    if uv is None or uv <= 0:
        return 0.0
    if precip_mm and precip_mm > 1.0:
        return 0.05  # rain clears beaches fast

    # Peak around 13.5h, sigma 2.5h
    time_f = bell(hour, 13.5, 2.5)
    # Weekend bump (Sat=5, Sun=6)
    weekend_f = 1.35 if dow >= 5 else 1.0
    # Warmth: 18°→0, 30°→1
    warmth = max(0, min((temp_c - 18) / 12, 1.0)) if temp_c is not None else 0.5
    # Clarity
    clarity = (100 - (cloud_pct or 0)) / 100
    # Wind penalty (light breeze fine, gale empties beach)
    wind_ok = max(0, 1 - (wind_kmh or 0) / 35)

    s = time_f * weekend_f * (warmth * 0.45 + clarity * 0.4 + wind_ok * 0.15)
    return round(min(1.0, s), 3)


def bucket(score_val):
    if score_val < 0.18: return "vazia"
    if score_val < 0.45: return "moderada"
    if score_val < 0.72: return "cheia"
    return "lotada"


def is_daytime(time_iso, sunrise_iso, sunset_iso):
    """Used to gate non-daylight hours as vazia regardless of formula."""
    try:
        t = datetime.fromisoformat(time_iso)
        sr = datetime.fromisoformat(sunrise_iso)
        ss = datetime.fromisoformat(sunset_iso)
        return sr <= t <= ss
    except Exception:
        return True


def main():
    conditions = json.load(open(CONDITIONS))
    now_dt = datetime.now()
    out = {"fetched_at": int(time.time()), "by_beach": {}}

    for p in conditions:
        h = p.get("hourly", {})
        sun = p.get("sun", {})
        times = h.get("time", [])
        if not times:
            continue

        # Hourly score over the 24h window we already have
        hourly_records = []
        for i, t in enumerate(times):
            try:
                dt = datetime.fromisoformat(t)
            except Exception:
                continue
            in_day = is_daytime(t, sun.get("sunrise"), sun.get("sunset"))
            if not in_day:
                s = 0.0
                b = "vazia"
            else:
                s = score(
                    hour=dt.hour,
                    dow=dt.weekday(),
                    temp_c=(h.get("temp_c") or [None])[i] if i < len(h.get("temp_c", [])) else None,
                    cloud_pct=(h.get("cloud_pct") or [None])[i] if i < len(h.get("cloud_pct", [])) else None,
                    wind_kmh=(h.get("wind_kmh") or [None])[i] if i < len(h.get("wind_kmh", [])) else None,
                    uv=(h.get("uv") or [None])[i] if i < len(h.get("uv", [])) else None,
                    precip_mm=(h.get("precip_mm") or [None])[i] if i < len(h.get("precip_mm", [])) else None,
                )
                b = bucket(s)
            hourly_records.append({"time": t, "score": s, "bucket": b})

        if not hourly_records:
            continue

        current = hourly_records[0]  # index 0 = current hour (we trim past hours upstream)
        # Find the peak hour and its bucket
        peak = max(hourly_records, key=lambda r: r["score"])

        out["by_beach"][p["id"]] = {
            "current": {
                "bucket": current["bucket"],
                "score": current["score"],
                "confidence": "estimativa",
            },
            "next_peak": {
                "time": peak["time"],
                "bucket": peak["bucket"],
                "score": peak["score"],
            },
            "hourly": hourly_records,
        }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=2)
    print(f"Wrote {OUT} — {len(out['by_beach'])} beaches", file=sys.stderr)
    for bid, info in out["by_beach"].items():
        c = info["current"]
        peak_t = info["next_peak"]["time"][11:16]
        print(f"  {bid:25} agora: {c['bucket']:9} ({c['score']:.2f}) · pico {peak_t} {info['next_peak']['bucket']}", file=sys.stderr)


if __name__ == "__main__":
    main()
