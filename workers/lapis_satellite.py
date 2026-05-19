"""LAPIS/UFAL satellite supplement for cloudy NE coast (PE/AL/BA/RN/CE).

STATUS: stub. LAPIS/UFAL hosts are not currently DNS-resolvable from
this environment; EUMETSAT View is JS-rendered. Worker writes
sem_dados records and documents access paths for later wiring.

Sources probed:
  - https://lapismet.com/         — DNS not resolvable (NXDOMAIN). Org
    publishes EUMETSAT-derived imagery for the NE; URLs change per
    product. Likely needs an institutional mirror once located.
  - https://www.lapis.ufal.br/    — DNS not resolvable. UFAL hosts the
    research group's site; previously published static PNG products.
  - https://view.eumetsat.int/    — public WMS viewer over Brazil
    region. Programmatic access via WMS GetMap (with layer name) is
    possible: e.g. msg_iodc_natural or copernicus_marine_ocean_color.
    Requires registering layer names + bbox per beach.

Output: data/lapis_satellite.json — one record per NE beach with
{image_url|null, turbidity_proxy|null, fetched_at, source, status}.

Next step: once the LAPIS host returns or a stable EUMETSAT WMS layer
is chosen, implement fetch_tile(lat,lng) producing a thumbnail under
web/lapis/{beach}/hoje.png mirroring satellite.py.
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "lapis_satellite.json")

NE_BEACHES = [
    "recife-boa-viagem",
    "ipojuca-porto-galinhas",
    "fortaleza-iracema-meireles",
    "maceio-pajucara",
    "salvador-itapua",
    "salvador-stella-maris",
    "morro-terceira",
    "natal-ponta-negra",
]

PROBED_SOURCES = [
    {"name": "lapismet", "url": "https://lapismet.com/",
     "note": "DNS NXDOMAIN at probe time"},
    {"name": "lapis_ufal", "url": "https://www.lapis.ufal.br/",
     "note": "DNS NXDOMAIN at probe time"},
    {"name": "eumetsat_view", "url": "https://view.eumetsat.int/",
     "note": "JS-rendered viewer; WMS GetMap viable with layer ids"},
]


def main():
    now = int(time.time())
    by_beach = {}
    for bid in NE_BEACHES:
        by_beach[bid] = {
            "image_url": None,
            "turbidity_proxy": None,
            "source": "lapis_eumetsat",
            "fetched_at": now,
            "status": "sem_dados",
        }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        "fetched_at": now,
        "by_beach": by_beach,
        "probed_sources": PROBED_SOURCES,
    }, open(OUT, "w"), ensure_ascii=False, indent=2)
    print(f"Wrote {OUT} — {len(by_beach)} NE beaches (stub, all sem_dados)", file=sys.stderr)


if __name__ == "__main__":
    main()
