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

# Keywords are matched on WORD BOUNDARIES (\b...\b), case-insensitive.
# Bare ambiguous aliases ("copa", "barra", "leme", "mar") are deliberately
# dropped — they collide with Copa do Mundo, Barra Funda, leme de barco, etc.
BEACH_TAGS = {
    "copacabana": ["copacabana"],
    "ipanema": ["ipanema"],
    "leblon": ["leblon"],
    "leme": ["praia do leme"],
    "arpoador": ["arpoador"],
    "barra": ["barra da tijuca"],
    "recreio": ["recreio dos bandeirantes", "recreio"],
    "prainha": ["prainha"],
    "general": ["litoral", "orla", "ressaca", "mar grosso", "balneabilidade"],
}

# If any of these appear, the item is rejected outright — common false-positive
# contexts where a beach-ish word shows up but the story isn't about the beach.
NEGATIVE_KEYWORDS = [
    "copa do mundo", "copa américa", "copa america", "copa do brasil",
    "libertadores", "sul-americana", "champions", "futebol", "campeonato",
    "barra funda", "barra mansa", "barra de chocolate", "barra de ferro",
    "barra pesada", "barra do piraí", "barra de são joão",
    "leme de", "tomar o leme",
    "praia grande", "praia clube", "praia do flamengo aterro",
    "praiana", "ferrugem",  # band/event noise
    "banda de ipanema", "bloco", "blocos de rua", "desfile",  # carnaval noise
    "garota de ipanema",  # the song / bar, not the beach
]

UA = "praiasmart/0.1"


def fetch(url):
    return subprocess.run(
        ["curl", "-sSfL", "-A", UA, "-m", "15", url],
        capture_output=True, text=True, check=True,
    ).stdout


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(s or ""))).strip()


# Beach-context words (word-boundary matched). "mar" alone removed — too noisy
# (Mar de Espanha, mar de gente, etc.). Require a genuine coastal signal.
BEACH_CONTEXT = ["praia", "praias", "orla", "areia", "ondas", "ressaca",
                 "litoral", "surf", "surfe", "maré", "marés", "balneabilidade",
                 "afogamento", "guarda-vidas", "salva-vidas", "banhistas"]


def _has_word(text, phrase):
    """Word-boundary, case-insensitive match. Multi-word phrases matched literally."""
    return re.search(r"\b" + re.escape(phrase) + r"\b", text, re.IGNORECASE) is not None


def tag_beaches(text):
    t = (text or "").lower()

    # Hard reject on negative keywords (football cups, other-city "Barra"s, etc.)
    if any(_has_word(t, neg) for neg in NEGATIVE_KEYWORDS):
        return []

    # Require a genuine coastal context word
    if not any(_has_word(t, c) for c in BEACH_CONTEXT):
        return []

    tags = [k for k, kws in BEACH_TAGS.items() if k != "general"
            and any(_has_word(t, kw) for kw in kws)]
    if tags:
        return tags

    # "general" fallback only for items with a STRONG coastal signal:
    # require 2+ distinct context words, so a single passing mention of
    # "praia" (e.g. "feriado na praia" in a traffic story) doesn't qualify.
    ctx_hits = sum(1 for c in BEACH_CONTEXT if _has_word(t, c))
    return ["general"] if ctx_hits >= 2 else []


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
