"""Pull INMET weather alerts, filter for Rio de Janeiro, write data/alerts.json."""
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "alerts.json")

RSS = "https://apiprevmet3.inmet.gov.br/avisos/rss"
UA = "praiasmart/0.1"

RIO_KEYWORDS = [
    "rio de janeiro", "litoral fluminense", "metropolitana do rio",
    "sul fluminense", "norte fluminense", "baixadas", "centro fluminense",
]

SEVERITY_ORDER = {
    "perigo potencial": 1,
    "perigo": 2,
    "grande perigo": 3,
}


def parse_field(html, label):
    m = re.search(
        rf"<th[^>]*>{re.escape(label)}</th>\s*<td>(.*?)</td>",
        html, re.S | re.I,
    )
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else None


def rio_match(area):
    if not area:
        return False
    a = area.lower()
    return any(k in a for k in RIO_KEYWORDS)


def main():
    raw = subprocess.run(
        ["curl", "-sSfL", "-A", UA, RSS],
        capture_output=True, text=True, timeout=30, check=True,
    ).stdout
    root = ET.fromstring(raw)

    now = datetime.now()
    alerts = []
    for item in root.iter("item"):
        desc = item.findtext("description") or ""
        area = parse_field(desc, "Área")
        if not rio_match(area):
            continue
        end = parse_field(desc, "Fim")
        try:
            if end and datetime.strptime(end.split(".")[0], "%Y-%m-%d %H:%M:%S") < now:
                continue
        except ValueError:
            pass
        sev = (parse_field(desc, "Severidade") or "").lower()
        alerts.append({
            "title": item.findtext("title"),
            "link": item.findtext("link"),
            "event": parse_field(desc, "Evento"),
            "severity": sev,
            "severity_rank": SEVERITY_ORDER.get(sev, 0),
            "start": parse_field(desc, "Início"),
            "end": parse_field(desc, "Fim"),
            "description": parse_field(desc, "Descrição"),
            "area": area,
        })

    alerts.sort(key=lambda a: -a["severity_rank"])

    json.dump({"fetched_at": int(time.time()), "alerts": alerts},
              open(OUT, "w"), ensure_ascii=False, indent=2)
    print(f"Wrote {OUT} — {len(alerts)} Rio alerts", file=sys.stderr)
    for a in alerts[:5]:
        print(f"  [{a['severity']}] {a['event']} — {a['start']} → {a['end']}", file=sys.stderr)


if __name__ == "__main__":
    main()
