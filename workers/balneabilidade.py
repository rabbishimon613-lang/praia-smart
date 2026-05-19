"""Scrape Brazilian beach water-quality (balneabilidade) reports.

Sources wired:
  - IMA-SC  (Santa Catarina) → floripa-barra-lagoa, balneario-camboriu,
            balneario-rincao. Weekly Fri PDF.
  - CETESB  (São Paulo)      → santos-gonzaga, guaruja-enseada,
            praia-grande-boqueirao. Weekly HTML map page.
  - INEA    (Rio de Janeiro) → copa-p5, leblon-mirante, sao-conrado,
            cabo-frio-forte. Weekly PDF linked from landing page.

morro-terceira (INEMA-BA) and natal-ponta-negra (IDEMA-RN) get sem_dados
placeholders for now — no clean URL pattern.

Stdlib + curl + pdftotext (poppler) only, to match other workers/ scripts.

Run:  python3 workers/balneabilidade.py
Out:  data/balneabilidade.json
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "balneabilidade.json")

UA = "praiasmart/0.1 (+balneabilidade)"
TIMEOUT = 30

# All beaches we care about — anything not filled in by a scraper
# gets a sem_dados stub at the end of build().
ALL_BEACH_IDS = [
    "copa-p5", "leblon-mirante", "sao-conrado", "cabo-frio-forte",
    "balneario-camboriu", "balneario-rincao", "floripa-barra-lagoa",
    "morro-terceira", "santos-gonzaga", "guaruja-enseada",
    "praia-grande-boqueirao", "natal-ponta-negra",
]

# Tier-2 sources we don't scrape yet: still report which agency would own them.
DEFAULT_SOURCE = {
    "morro-terceira": "INEMA",
    "natal-ponta-negra": "IDEMA",
}


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def curl(url, binary=False):
    """Fetch a URL via curl. Returns text (decoded tolerantly) or bytes."""
    args = ["curl", "-sSfL", "-A", UA, "-m", str(TIMEOUT), url]
    raw = subprocess.run(args, capture_output=True, check=True,
                         timeout=TIMEOUT + 5).stdout
    if binary:
        return raw
    # Try utf-8 then latin-1 (CETESB and many .gov.br sites are cp1252/latin-1).
    for enc in ("utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def pdf_to_text(pdf_bytes):
    """Use poppler's pdftotext (layout-preserving) to extract text."""
    p = subprocess.run(
        ["pdftotext", "-layout", "-nopgbrk", "-", "-"],
        input=pdf_bytes, capture_output=True, timeout=30, check=True,
    )
    return p.stdout.decode("utf-8", errors="replace")


def classify(token):
    """Map agency status text → our normalized status."""
    if not token:
        return None
    t = token.lower()
    if "própr" in t or "propr" in t or t.strip() in {"p", "ok"}:
        # CETESB uses "Própria" / IMA uses "PRÓPRIA" / INEA same.
        return "propria"
    if "impr" in t or "imprópr" in t or t.strip() in {"i"}:
        return "impropria"
    if "alerta" in t or "atenção" in t or "atencao" in t:
        return "alerta"
    return None


# -----------------------------------------------------------------------------
# IMA-SC
# -----------------------------------------------------------------------------
# Weekly PDF: https://balneabilidade.ima.sc.gov.br/relatorio/downloadPDF/YYYY-MM-DD
# Try recent Fridays going back ~5 weeks.

IMA_NAME_MAP = {
    # substring match against PDF row text → beach_id
    "barra da lagoa": "floripa-barra-lagoa",
    "balneário camboriú": "balneario-camboriu",
    "balneario camboriu": "balneario-camboriu",
    "rincão": "balneario-rincao",
    "rincao": "balneario-rincao",
}
IMA_PREFERRED_POINT = {
    # If multiple sample points hit, prefer one matching this hint
    "balneario-camboriu": "marambaia",  # matches Hotel Marambaia in postos.csv
    "floripa-barra-lagoa": None,
    "balneario-rincao": None,
}


def _recent_fridays(n=6):
    today = date.today()
    # weekday(): Mon=0 ... Fri=4
    offset = (today.weekday() - 4) % 7
    last_fri = today - timedelta(days=offset)
    return [last_fri - timedelta(days=7 * i) for i in range(n)]


def fetch_ima_sc():
    out = {}
    for d in _recent_fridays(6):
        url = f"https://balneabilidade.ima.sc.gov.br/relatorio/downloadPDF/{d.isoformat()}"
        try:
            pdf = curl(url, binary=True)
        except subprocess.CalledProcessError:
            continue
        if not pdf.startswith(b"%PDF"):
            continue
        try:
            text = pdf_to_text(pdf)
        except Exception as e:
            print(f"  IMA-SC: pdftotext failed for {d}: {e}", file=sys.stderr)
            continue
        report_date = d.isoformat()
        print(f"  IMA-SC: parsing {d}", file=sys.stderr)
        out = _parse_ima_text(text, url, report_date)
        if out:
            return out
    return out


def _parse_ima_text(text, url, report_date):
    """IMA PDFs list lines like:
        Florianópolis  Barra da Lagoa  Em frente ao posto 7  PRÓPRIA
    We do a best-effort substring match per beach id.
    """
    out = {}
    candidates = {bid: [] for bid in set(IMA_NAME_MAP.values())}
    for line in text.splitlines():
        low = line.lower()
        status = None
        if "própr" in low or "propr" in low:
            status = "propria" if "impr" not in low else "impropria"
        elif "impróp" in low or "improp" in low:
            status = "impropria"
        if not status:
            continue
        for needle, bid in IMA_NAME_MAP.items():
            if needle in low:
                candidates[bid].append((line.strip(), status))
                break
    for bid, hits in candidates.items():
        if not hits:
            continue
        chosen = hits[0]
        hint = IMA_PREFERRED_POINT.get(bid)
        if hint:
            for line, st in hits:
                if hint in line.lower():
                    chosen = (line, st)
                    break
        line, status = chosen
        out[bid] = {
            "status": status,
            "source": "IMA-SC",
            "report_date": report_date,
            "ecoli": None,
            "url": url,
            "confidence": "oficial",
        }
    return out


# -----------------------------------------------------------------------------
# CETESB
# -----------------------------------------------------------------------------

CETESB_BASE = "https://sistemasinter.cetesb.sp.gov.br/praias/mapa_praias/respraia1.asp"
CETESB_URL = CETESB_BASE  # for entry "url" field

# CETESB groups beaches per-city; we hit one URL per relevant city.
# city_code → (CETESB ?praia= code, list of (beach_name_substring, beach_id))
CETESB_CITIES = [
    ("ST", [
        ("gonzaga", "santos-gonzaga"),
    ]),
    ("GJ", [
        # In CETESB's Guarujá list, the Enseada points appear as
        # "ENSEADA-..." (Av. Atlântica matches the Enseada P11 area roughly).
        # First-hit on plain "enseada" is fine — they're contiguous.
        ("enseada", "guaruja-enseada"),
    ]),
    ("PG", [
        ("boqueir", "praia-grande-boqueirao"),
    ]),
]


_CETESB_ICON_STATUS = {
    "verde": "propria",
    "vermelha": "impropria",
    "vermelho": "impropria",
    "amarela": "alerta",
    "amarelo": "alerta",
}


def fetch_cetesb():
    # Pair each status-icon img with the *next* beach-name <td>.
    pattern = re.compile(
        r'src="(verde|vermelha|vermelho|amarela|amarelo)\.gif"'
        r'.*?<td[^>]*>(?:\s*<[^>]+>\s*)*\s*([A-Za-zÀ-ÿ0-9][^<]{1,60}?)\s*<',
        re.I | re.S,
    )
    out = {}
    report_date = None
    for code, beaches in CETESB_CITIES:
        url = f"{CETESB_BASE}?praia={code}"
        try:
            html = curl(url)
        except subprocess.CalledProcessError as e:
            print(f"  CETESB {code}: HTTP err {e}", file=sys.stderr)
            continue
        if report_date is None:
            m = re.search(r"(\d{2}/\d{2}/\d{4})", html)
            if m:
                try:
                    report_date = datetime.strptime(
                        m.group(1), "%d/%m/%Y").date().isoformat()
                except ValueError:
                    pass
        pairs = pattern.findall(html)
        for needle, bid in beaches:
            if bid in out:
                continue
            for icon, name in pairs:
                low = name.lower().strip()
                if needle in low:
                    status = _CETESB_ICON_STATUS.get(icon.lower())
                    if not status:
                        continue
                    out[bid] = {
                        "status": status,
                        "source": "CETESB",
                        "report_date": report_date,
                        "ecoli": None,
                        "url": url,
                        "confidence": "oficial",
                    }
                    break
    return out


# -----------------------------------------------------------------------------
# INEA
# -----------------------------------------------------------------------------

INEA_LANDING = "https://www.inea.rj.gov.br/ar-agua-e-solo/balneabilidade-das-praias/"

INEA_NAME_MAP = {
    # match (beach_substring, point_substring) → beach_id
    ("copacabana", "p5"): "copa-p5",
    ("copacabana", "posto 5"): "copa-p5",
    ("leblon", "mirante"): "leblon-mirante",
    ("leblon", "leblon"): "leblon-mirante",     # fallback if only one Leblon point
    ("são conrado", ""): "sao-conrado",
    ("sao conrado", ""): "sao-conrado",
    ("pepino", ""): "sao-conrado",
    ("forte", "cabo frio"): "cabo-frio-forte",
    ("cabo frio", "forte"): "cabo-frio-forte",
}


def fetch_inea():
    html = curl(INEA_LANDING)
    # Find candidate PDF links — prefer ones containing "boletim" or "semanal".
    links = re.findall(r'href="([^"]+\.pdf[^"]*)"', html, re.I)
    if not links:
        print("  INEA: no PDF links on landing page", file=sys.stderr)
        return {}
    ranked = sorted(
        set(links),
        key=lambda u: (
            ("boletim" in u.lower() or "semanal" in u.lower()),
            "2026" in u,
            "2025" in u,
        ),
        reverse=True,
    )
    last_err = None
    for u in ranked[:5]:
        if u.startswith("/"):
            u = "https://www.inea.rj.gov.br" + u
        try:
            pdf = curl(u, binary=True)
        except subprocess.CalledProcessError as e:
            last_err = e
            continue
        if not pdf.startswith(b"%PDF"):
            continue
        try:
            text = pdf_to_text(pdf)
        except Exception as e:
            last_err = e
            continue
        print(f"  INEA: parsing {u}", file=sys.stderr)
        out = _parse_inea_text(text, u)
        if out:
            return out
    if last_err:
        print(f"  INEA: last error {last_err}", file=sys.stderr)
    return {}


def _parse_inea_text(text, url):
    # Pull a date if present (DD/MM/YYYY).
    m = re.search(r"(\d{2}/\d{2}/\d{4})", text)
    report_date = None
    if m:
        try:
            report_date = datetime.strptime(m.group(1), "%d/%m/%Y").date().isoformat()
        except ValueError:
            pass

    out = {}
    for line in text.splitlines():
        low = line.lower()
        status = classify(low)
        if not status:
            continue
        for (beach_kw, point_kw), bid in INEA_NAME_MAP.items():
            if beach_kw not in low:
                continue
            if point_kw and point_kw not in low:
                continue
            if bid in out:
                # Prefer rows with the more-specific point keyword
                if not point_kw:
                    continue
            out[bid] = {
                "status": status,
                "source": "INEA",
                "report_date": report_date,
                "ecoli": None,
                "url": url,
                "confidence": "oficial",
            }
            break
    return out


# -----------------------------------------------------------------------------
# Build
# -----------------------------------------------------------------------------

def build():
    by_beach = {}

    for name, fn in [("IMA-SC", fetch_ima_sc),
                     ("CETESB", fetch_cetesb),
                     ("INEA",   fetch_inea)]:
        try:
            res = fn() or {}
            print(f"  {name}: {len(res)} beaches resolved", file=sys.stderr)
            by_beach.update(res)
        except Exception as e:
            print(f"  {name}: ERR {e}", file=sys.stderr)

    # Fill sem_dados stubs for anything missing.
    for bid in ALL_BEACH_IDS:
        if bid in by_beach:
            continue
        by_beach[bid] = {
            "status": "sem_dados",
            "source": DEFAULT_SOURCE.get(bid, "—"),
            "report_date": None,
            "ecoli": None,
            "url": None,
            "confidence": "estimativa",
        }

    payload = {"fetched_at": int(time.time()), "by_beach": by_beach}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(payload, open(OUT, "w"), ensure_ascii=False, indent=2)

    real = sum(1 for v in by_beach.values() if v["status"] != "sem_dados")
    print(f"Wrote {OUT} — {real}/{len(by_beach)} with real data", file=sys.stderr)
    for bid, v in by_beach.items():
        print(f"  {bid:28} {v['status']:10} {v['source']}", file=sys.stderr)


if __name__ == "__main__":
    build()
