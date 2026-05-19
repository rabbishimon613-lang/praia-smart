"""Scrape Rio lifeguard bandeira (flag) status per posto.

STATUS: stub. No public live feed of CBMERJ flag colors per posto exists
as of investigation date. Writes all-sem_dados while documenting probed
sources for future scraping work.

Sources probed:
  - https://www.orlario.com.br/  : 200 OK. Has surfview.com.br iframe
    embeds (e.g. /api/embed/postoQuatroOrlaRio) — live cameras, no
    structured bandeira JSON. A future scrape could OCR camera frames.
  - https://cor.rio/             : 200 OK. WordPress news portal,
    no machine-readable feed for posto-level flags. Some posts mention
    "câmeras com superzoom" for monitoring — manual viewing only.
  - https://www.cbmerj.rj.gov.br/: 200 OK. Public-affairs site. No
    bandeira API. Bombeiros publish flag status only via radio/onsite.
  - https://www.rio.rj.gov.br/   : portal, no praias data endpoint.

Blocker: no agency publishes posto-level bandeira colors over HTTP.
When/if Orla Rio or CBMERJ exposes a JSON feed, replace process_beach()
to map bandeira values into {verde, amarela, vermelha}.
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "orla_rio.json")

# Rio beach IDs to cover (matches postos.csv where applicable)
RIO_BEACHES = [
    "copa-p5",
    "leblon-mirante",
    "sao-conrado",
    "ipanema-posto-9",
    "barra-tijuca-posto-3",
]

PROBED_SOURCES = [
    {"agency": "orla_rio", "url": "https://www.orlario.com.br/",
     "note": "surfview camera iframes, no structured flag data"},
    {"agency": "cor_rio", "url": "https://cor.rio/",
     "note": "WordPress news; no posto-level feed"},
    {"agency": "cbmerj", "url": "https://www.cbmerj.rj.gov.br/",
     "note": "no bandeira API; status only on-site/radio"},
]


def main():
    now = int(time.time())
    by_beach = {}
    for bid in RIO_BEACHES:
        by_beach[bid] = {
            "bandeira": "sem_dados",
            "source": "none",
            "fetched_at": now,
            "url": None,
        }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        "fetched_at": now,
        "by_beach": by_beach,
        "probed_sources": PROBED_SOURCES,
    }, open(OUT, "w"), ensure_ascii=False, indent=2)
    print(f"Wrote {OUT} — {len(by_beach)} beaches, all sem_dados (stub)", file=sys.stderr)


if __name__ == "__main__":
    main()
