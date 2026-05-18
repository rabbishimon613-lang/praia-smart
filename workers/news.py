"""Aggregate G1 Rio, Catraca Livre, Veja Rio RSS, filter for beach content.

Writes data/news.json with items tagged by matched beach/posto.
"""
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from html import unescape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "news.json")

FEEDS = [
    ("g1-rio", "https://g1.globo.com/rss/g1/rio-de-janeiro/"),
    ("catraca-livre", "https://catracalivre.com.br/feed/"),
    ("veja-rio", "https://vejario.abril.com.br/feed/"),
]

BEACH_TAGS = {
    "copacabana": ["copacabana", "copa"],
    "ipanema": ["ipanema"],
    "leblon": ["leblon"],
    "leme": ["leme"],
    "arpoador": ["arpoador"],
    "barra": ["barra da tijuca", "barra"],
    "recreio": ["recreio"],
    "prainha": ["prainha"],
    "general": ["praia", "litoral", "orla", "areia", "ressaca", "mar grosso"],
}

UA = "praiasmart/0.1"


def fetch(url):
    return subprocess.run(
        ["curl", "-sSfL", "-A", UA, "-m", "15", url],
        capture_output=True, text=True, check=True,
    ).stdout


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(s or ""))).strip()


BEACH_CONTEXT = ["praia", "orla", "areia", "mar ", "onda", "ressaca",
                 "litoral", "surf", "marés", "areal"]


def tag_beaches(text):
    t = text.lower()
    has_beach_context = any(c in t for c in BEACH_CONTEXT)
    if not has_beach_context:
        return []
    tags = [k for k, kws in BEACH_TAGS.items() if k != "general"
            and any(kw in t for kw in kws)]
    return tags or ["general"]


def parse_feed(source, xml):
    root = ET.fromstring(xml)
    items = []
    for item in root.iter("item"):
        title = strip_html(item.findtext("title") or "")
        desc = strip_html(item.findtext("description") or "")
        link = (item.findtext("link") or "").strip()
        pub = item.findtext("pubDate") or ""
        tags = tag_beaches(title + " " + desc)
        if not tags:
            continue
        items.append({
            "source": source,
            "title": title,
            "summary": desc[:240],
            "link": link,
            "pub_date": pub,
            "beaches": tags,
        })
    return items


def main():
    all_items = []
    for source, url in FEEDS:
        try:
            xml = fetch(url)
            items = parse_feed(source, xml)
            print(f"  {source}: {len(items)} beach items", file=sys.stderr)
            all_items.extend(items)
        except Exception as e:
            print(f"  {source}: ERR {e}", file=sys.stderr)

    # Dedupe by link
    seen = set()
    dedup = []
    for it in all_items:
        if it["link"] in seen:
            continue
        seen.add(it["link"])
        dedup.append(it)

    json.dump({"fetched_at": int(time.time()), "items": dedup},
              open(OUT, "w"), ensure_ascii=False, indent=2)
    print(f"Wrote {OUT} — {len(dedup)} unique items", file=sys.stderr)
    for it in dedup[:8]:
        print(f"  [{','.join(it['beaches'])}] {it['source']:14} {it['title'][:80]}", file=sys.stderr)


if __name__ == "__main__":
    main()
