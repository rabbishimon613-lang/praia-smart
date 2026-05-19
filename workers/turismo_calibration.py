"""Pull monthly visitor stats from state Observatórios de Turismo.

STATUS: stub. The state observatórios publish PDF/XLSX bulletins behind
WordPress portals — no JSON API. Worker writes sem_dados records and
documents the publish cadence so a future PDF-parser can backfill.

Sources probed:
  - https://www.observatorio.turismo.ba.gov.br/  (Bahia)   — TIMEOUT;
    portal slow, publishes monthly PDF "Boletim do Turismo".
  - https://www.setur.ce.gov.br/observatorio/    (Ceará)   — 403 to
    curl UA; requires browser-like headers. Publishes XLSX bulletins.
  - https://www.observatoriodoturismo.sp.gov.br/ (São Paulo) — known
    portal, publishes PDF "Painel de Indicadores".
  - https://setur.rj.gov.br/                     (Rio de Janeiro)
  - https://www.observatorio.tur.pe.gov.br/      (Pernambuco) — host
    sometimes unresolved; publishes "Boletim Setur-PE".

Output: data/turismo_calibration.json. Cities covered: salvador,
fortaleza, sao-paulo, rio-de-janeiro, recife, maceio.

Next step: replace fetch_*() stubs with PDF/XLSX scrapers (camelot/
openpyxl) once a current bulletin URL is pinned per state.
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "turismo_calibration.json")

CITIES = {
    "salvador":       {"state": "BA", "source": "https://www.observatorio.turismo.ba.gov.br/"},
    "fortaleza":      {"state": "CE", "source": "https://www.setur.ce.gov.br/observatorio/"},
    "sao-paulo":      {"state": "SP", "source": "https://www.observatoriodoturismo.sp.gov.br/"},
    "rio-de-janeiro": {"state": "RJ", "source": "https://setur.rj.gov.br/"},
    "recife":         {"state": "PE", "source": "https://www.observatorio.tur.pe.gov.br/"},
    "maceio":         {"state": "AL", "source": "https://www.cultura.al.gov.br/turismo/"},
}


def fetch_city(city, meta):
    """Stub: returns sem_dados record. Replace with real scraper later."""
    return {
        "monthly_visitors": None,
        "month": None,
        "trend_yoy_pct": None,
        "source": meta["source"],
        "state": meta["state"],
        "status": "sem_dados",
    }


def main():
    now = int(time.time())
    by_city = {city: fetch_city(city, meta) for city, meta in CITIES.items()}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"fetched_at": now, "by_city": by_city},
              open(OUT, "w"), ensure_ascii=False, indent=2)
    print(f"Wrote {OUT} — {len(by_city)} cities (stub, all sem_dados)", file=sys.stderr)


if __name__ == "__main__":
    main()
