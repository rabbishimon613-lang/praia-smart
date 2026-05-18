"""AISStream collector → data/ships.json (inverse index per beach).

Two modes:
  python ships.py --once    one-shot: collect ~90s, write, exit
  python ships.py           daemon: stay connected, refresh every 60s, reconnect on failure
"""
import argparse
import asyncio
import csv
import json
import math
import os
import ssl
import sys
import time

import certifi
import websockets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTOS = os.path.join(ROOT, "postos.csv")
OUT = os.path.join(ROOT, "data", "ships.json")
KEY = os.environ.get("AISSTREAM_KEY")
URL = "wss://stream.aisstream.io/v0/stream"
SSL_CTX = ssl.create_default_context(cafile=certifi.where())

RADIUS_KM = 50.0
STALE_AFTER_S = 20 * 60   # forget ships not seen in 20 minutes
FLUSH_EVERY_S = 60        # write JSON every minute
ONCE_COLLECT_S = 90       # one-shot: collect this long then exit

# Brazilian coast bbox covering all current beaches with margin
NATIONAL_BBOX = [[[-30.0, -50.0], [-5.0, -34.0]]]


def ship_type_label(code):
    if code is None: return "—"
    if code == 30: return "pesqueiro"
    if code in (31, 32, 52): return "rebocador"
    if code in (33, 34): return "draga"
    if code == 35: return "militar"
    if code in (36, 37): return "iate"
    if 40 <= code <= 49: return "rápido"
    if 50 <= code <= 59: return "passageiros"
    if 60 <= code <= 69: return "cruzeiro" if code == 60 else "passageiros"
    if 70 <= code <= 79: return "cargueiro"
    if 80 <= code <= 89: return "petroleiro"
    return "outro"


def nav_status_label(code):
    return {
        0: "navegando", 1: "ancorado", 2: "sem comando", 3: "manobra limitada",
        4: "draft restrito", 5: "atracado", 6: "encalhado",
        7: "pescando", 8: "à vela",
    }.get(code, "—")


def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def bearing(lat1, lng1, lat2, lng2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lng2 - lng1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1)*math.sin(p2) - math.sin(p1)*math.cos(p2)*math.cos(dl)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def compass(deg):
    if deg is None: return "·"
    dirs = ["N","NE","L","SE","S","SO","O","NO"]
    return dirs[int(((deg + 22.5) % 360) // 45)]


def load_beaches():
    beaches = []
    for row in csv.DictReader(open(POSTOS)):
        beaches.append({
            "id": row["id"], "beach": row["beach"], "posto": row["posto"],
            "lat": float(row["lat"]), "lng": float(row["lng"]),
        })
    return beaches


def write_index(ships, beaches):
    """Build per-beach inverse index of ships within RADIUS_KM."""
    now = time.time()
    # Prune stale
    fresh = {m: s for m, s in ships.items() if now - s.get("ts", 0) < STALE_AFTER_S}

    index = {b["id"]: [] for b in beaches}
    for mmsi, s in fresh.items():
        if s.get("lat") is None or s.get("lng") is None:
            continue
        for b in beaches:
            d = haversine_km(b["lat"], b["lng"], s["lat"], s["lng"])
            if d > RADIUS_KM:
                continue
            brg = bearing(b["lat"], b["lng"], s["lat"], s["lng"])
            index[b["id"]].append({
                "mmsi": mmsi,
                "name": (s.get("name") or "").strip() or None,
                "type": s.get("type_label"),
                "type_code": s.get("type_code"),
                "status": s.get("nav_label"),
                "speed_kn": round(s.get("sog", 0), 1) if s.get("sog") is not None else None,
                "heading": s.get("heading"),
                "dest": (s.get("dest") or "").strip() or None,
                "callsign": (s.get("callsign") or "").strip() or None,
                "lat": round(s["lat"], 4), "lng": round(s["lng"], 4),
                "dist_km": round(d, 1),
                "bearing": round(brg),
                "compass": compass(brg),
                "last_seen": int(s["ts"]),
            })

    for bid in index:
        index[bid].sort(key=lambda x: x["dist_km"])

    out = {
        "fetched_at": int(now),
        "radius_km": RADIUS_KM,
        "total_ships": len(fresh),
        "by_beach": index,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=2)
    return out


async def collect(stop_after_s=None, flush_cb=None):
    if not KEY:
        sys.exit("ERR: AISSTREAM_KEY env var not set. `source .env` first.")
    ships = {}  # mmsi -> {lat, lng, sog, heading, name, type_code, type_label, ts, ...}
    deadline = time.time() + stop_after_s if stop_after_s else None
    next_flush = time.time() + FLUSH_EVERY_S

    while True:
        try:
            async with websockets.connect(URL, ssl=SSL_CTX, ping_interval=30) as ws:
                await ws.send(json.dumps({
                    "APIKey": KEY,
                    "BoundingBoxes": NATIONAL_BBOX,
                    "FilterMessageTypes": ["PositionReport", "ShipStaticData", "StaticDataReport"],
                }))
                print(f"[ships] connected, subscribed to BR coast", file=sys.stderr)

                while True:
                    if deadline and time.time() > deadline:
                        return ships
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    except asyncio.TimeoutError:
                        if flush_cb and time.time() > next_flush:
                            flush_cb(ships)
                            next_flush = time.time() + FLUSH_EVERY_S
                        continue

                    msg = json.loads(raw)
                    meta = msg.get("MetaData", {}) or {}
                    mtype = msg.get("MessageType")
                    mmsi = meta.get("MMSI") or meta.get("MMSI_String")
                    if mmsi is None:
                        continue
                    s = ships.setdefault(int(mmsi), {})
                    s["ts"] = time.time()

                    if mtype == "PositionReport":
                        pr = msg["Message"]["PositionReport"]
                        s["lat"] = pr.get("Latitude")
                        s["lng"] = pr.get("Longitude")
                        s["sog"] = pr.get("Sog")
                        s["heading"] = pr.get("TrueHeading") if pr.get("TrueHeading", 511) != 511 else None
                        s["nav_code"] = pr.get("NavigationalStatus")
                        s["nav_label"] = nav_status_label(pr.get("NavigationalStatus"))
                        if not s.get("name"):
                            s["name"] = meta.get("ShipName")

                    elif mtype in ("ShipStaticData", "StaticDataReport"):
                        sd = msg["Message"].get("ShipStaticData") or msg["Message"].get("StaticDataReport") or {}
                        s["name"] = sd.get("Name") or s.get("name") or meta.get("ShipName")
                        s["type_code"] = sd.get("Type")
                        s["type_label"] = ship_type_label(sd.get("Type"))
                        s["dest"] = sd.get("Destination")
                        s["callsign"] = sd.get("CallSign")
                        s["length"] = (sd.get("Dimension", {}).get("A", 0) +
                                       sd.get("Dimension", {}).get("B", 0)) or None

                    if not s.get("type_label"):
                        s["type_label"] = "—"

                    if flush_cb and time.time() > next_flush:
                        flush_cb(ships)
                        next_flush = time.time() + FLUSH_EVERY_S

        except websockets.exceptions.ConnectionClosed:
            print("[ships] connection closed, reconnecting in 5s", file=sys.stderr)
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[ships] error: {e}, reconnecting in 10s", file=sys.stderr)
            await asyncio.sleep(10)


async def run_once():
    beaches = load_beaches()
    print(f"[ships] one-shot collection for {ONCE_COLLECT_S}s", file=sys.stderr)
    ships = await collect(stop_after_s=ONCE_COLLECT_S)
    summary = write_index(ships, beaches)
    print(f"[ships] {summary['total_ships']} ships, by beach:", file=sys.stderr)
    for bid, lst in summary["by_beach"].items():
        if lst:
            print(f"  {bid:25} {len(lst)} ships, closest {lst[0]['dist_km']}km", file=sys.stderr)


async def run_daemon():
    beaches = load_beaches()
    def flush(ships):
        summary = write_index(ships, beaches)
        print(f"[ships] flushed: {summary['total_ships']} ships tracked", file=sys.stderr)
    await collect(stop_after_s=None, flush_cb=flush)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    asyncio.run(run_once() if args.once else run_daemon())


if __name__ == "__main__":
    main()
