"""Fetch current conditions for every posto in one shot via Open-Meteo.

Writes data/conditions.json with one entry per posto containing surf,
weather, water, air quality, sun. No API key needed.
"""
import csv
import json
import os
import subprocess
import sys
import time
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTOS = os.path.join(ROOT, "postos.csv")
OUT = os.path.join(ROOT, "data", "conditions.json")

FORECAST = "https://api.open-meteo.com/v1/forecast"
MARINE = "https://marine-api.open-meteo.com/v1/marine"
AIRQ = "https://air-quality-api.open-meteo.com/v1/air-quality"
UA = "praiasmart/0.1"


def curl_json(url):
    raw = subprocess.run(
        ["curl", "-sSfL", "-A", UA, url],
        capture_output=True, text=True, timeout=30, check=True,
    ).stdout
    return json.loads(raw)


def batch(url, lats, lngs, **params):
    qs = {
        "latitude": ",".join(str(x) for x in lats),
        "longitude": ",".join(str(x) for x in lngs),
        "timezone": "America/Sao_Paulo",
        **params,
    }
    return curl_json(url + "?" + urllib.parse.urlencode(qs))


def normalize(result):
    """Open-Meteo returns a single object for one location, list for many."""
    return result if isinstance(result, list) else [result]


def next_extrema(times, levels, now_iso):
    """Return (next_high, next_low) as {time, height} from hourly series."""
    if not times or not levels:
        return None, None
    # Find first index at or after now
    start = next((i for i, t in enumerate(times) if t >= now_iso), 0)
    high = low = None
    for i in range(start + 1, len(levels) - 1):
        if levels[i] is None or levels[i - 1] is None or levels[i + 1] is None:
            continue
        if not high and levels[i] > levels[i - 1] and levels[i] > levels[i + 1]:
            high = {"time": times[i], "height_m": round(levels[i], 2)}
        if not low and levels[i] < levels[i - 1] and levels[i] < levels[i + 1]:
            low = {"time": times[i], "height_m": round(levels[i], 2)}
        if high and low:
            break
    return high, low


def main():
    postos = list(csv.DictReader(open(POSTOS)))
    lats = [float(p["lat"]) for p in postos]
    lngs = [float(p["lng"]) for p in postos]

    print(f"Fetching for {len(postos)} postos...", file=sys.stderr)

    forecast = normalize(batch(
        FORECAST, lats, lngs,
        current="temperature_2m,wind_speed_10m,wind_direction_10m,uv_index,cloud_cover,precipitation",
        hourly="temperature_2m,wind_speed_10m,wind_direction_10m,uv_index,cloud_cover,precipitation",
        daily="sunrise,sunset",
        forecast_days=2,
    ))
    marine = normalize(batch(
        MARINE, lats, lngs,
        current="wave_height,wave_period,wave_direction,sea_surface_temperature",
        hourly="wave_height,wave_period,sea_level_height_msl",
        forecast_days=2,
    ))
    airq = normalize(batch(
        AIRQ, lats, lngs,
        current="pm10,pm2_5,european_aqi",
    ))

    now_iso = time.strftime("%Y-%m-%dT%H:%M", time.localtime())
    out = []
    for p, f, m, a in zip(postos, forecast, marine, airq):
        fc, mc, ac = f.get("current", {}), m.get("current", {}), a.get("current", {})
        daily = f.get("daily", {})
        mh = m.get("hourly", {})
        fh = f.get("hourly", {})
        next_high, next_low = next_extrema(
            mh.get("time", []), mh.get("sea_level_height_msl", []), now_iso
        )

        # Keep next 24h hourly arrays starting from current hour
        times = mh.get("time", [])
        start_i = next((i for i, t in enumerate(times) if t >= now_iso), 0)
        end_i = start_i + 24
        hourly = {
            "time": times[start_i:end_i],
            "tide_m": mh.get("sea_level_height_msl", [])[start_i:end_i],
            "wave_m": mh.get("wave_height", [])[start_i:end_i],
            "wave_period_s": mh.get("wave_period", [])[start_i:end_i],
            "temp_c": fh.get("temperature_2m", [])[start_i:end_i],
            "wind_kmh": fh.get("wind_speed_10m", [])[start_i:end_i],
            "wind_dir": fh.get("wind_direction_10m", [])[start_i:end_i],
            "uv": fh.get("uv_index", [])[start_i:end_i],
            "cloud_pct": fh.get("cloud_cover", [])[start_i:end_i],
            "precip_mm": fh.get("precipitation", [])[start_i:end_i],
        }
        out.append({
            "id": p["id"],
            "beach": p["beach"],
            "posto": p["posto"],
            "state": p.get("state") or "?",
            "lat": float(p["lat"]),
            "lng": float(p["lng"]),
            "youtube_id": p["youtube_id"] or None,
            "fetched_at": int(time.time()),
            "weather": {
                "air_temp_c": fc.get("temperature_2m"),
                "wind_kmh": fc.get("wind_speed_10m"),
                "wind_dir": fc.get("wind_direction_10m"),
                "uv": fc.get("uv_index"),
                "cloud_pct": fc.get("cloud_cover"),
                "precip_mm": fc.get("precipitation"),
            },
            "surf": {
                "wave_height_m": mc.get("wave_height"),
                "wave_period_s": mc.get("wave_period"),
                "wave_dir": mc.get("wave_direction"),
            },
            "water": {
                "sea_temp_c": mc.get("sea_surface_temperature"),
                "next_high_tide": next_high,
                "next_low_tide": next_low,
            },
            "air": {
                "pm25": ac.get("pm2_5"),
                "pm10": ac.get("pm10"),
                "aqi": ac.get("european_aqi"),
            },
            "sun": {
                "sunrise": daily.get("sunrise", [None])[0],
                "sunset": daily.get("sunset", [None])[0],
            },
            "hourly": hourly,
        })

    json.dump(out, open(OUT, "w"), indent=2)
    print(f"Wrote {OUT} ({len(out)} postos)", file=sys.stderr)


if __name__ == "__main__":
    main()
