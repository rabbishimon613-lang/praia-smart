"""Per-beach 'webcam ao vivo' landing pages.

Generates web/<city-slug>/webcam-ao-vivo.html for each beach that has a
youtube_id. Slugs come from build.CITY_SLUG_BY_BEACH so they stay aligned
with the homepage and sitemap.

This is the SEO landing-page play for queries like "webcam copacabana ao
vivo", "câmera ao vivo morro de são paulo", etc.
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import (
    SITE_URL, PRECONNECT_HTML, FAVICON_HTML, FOOTER_HTML, FOOTER_CSS,
    NEARBY_CSS, CITY_SLUG_BY_BEACH,
    render_nearby_section, breadcrumb_jsonld, video_object_jsonld,
    wind_arrow, fmt, uv_label,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "conditions.json")
BALNE = os.path.join(ROOT, "data", "balneabilidade.json")
OUT_ROOT = os.path.join(ROOT, "web")


CSS = """
:root {
  --paper:#F4EFE4; --paper-warm:#F9F4E8; --card:#FFFFFF;
  --ink:#1F3F4D; --ink-soft:#577485; --mute:#94A8B4;
  --line:#E6DCC8;
  --accent:#E8895E; --surf:#E8895E; --swim:#5A9FB5; --sun:#E5B86A; --shade:#7C9183;
  --good:#5BB48A; --bad:#D44A2A;
  --font-sans:"Plus Jakarta Sans",-apple-system,BlinkMacSystemFont,system-ui,sans-serif;
  --font-serif:"Instrument Serif","Times New Roman",serif;
  --font-mono:"JetBrains Mono",ui-monospace,"SF Mono",Menlo,monospace;
  --pad:16px;
}
* { box-sizing: border-box; }
html, body {
  margin:0; padding:0;
  background:
    radial-gradient(900px 600px at 20% 0%, #f1ecdf 0%, transparent 50%),
    radial-gradient(800px 700px at 100% 30%, #e5eef2 0%, transparent 55%),
    linear-gradient(180deg, #efe9da 0%, #e9e4d2 100%);
  background-attachment: fixed;
  color: var(--ink); font-family: var(--font-sans);
  font-size: 15px; line-height: 1.45;
  -webkit-font-smoothing: antialiased;
}
a { color: inherit; text-decoration: none; }

.topbar {
  position: sticky; top: 0; z-index: 10;
  background: linear-gradient(180deg, var(--paper) 70%, rgba(244,239,228,0.85) 100%);
  backdrop-filter: blur(10px);
  padding: 10px var(--pad);
  padding-top: calc(10px + env(safe-area-inset-top));
  border-bottom: 1px solid rgba(230,220,200,0.7);
  display: flex; align-items: center; gap: 12px;
}
.back-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; border-radius: 999px;
  background: var(--card); border: 1px solid var(--line);
  color: var(--accent); flex: 0 0 auto;
}
.wordmark { display: inline-flex; align-items: baseline; gap: 4px; margin-left: auto; }
.wordmark .wm-praia {
  font-family: var(--font-serif); font-style: italic; font-weight: 400;
  font-size: 28px; color: var(--accent); line-height: 1;
}
.wordmark .wm-smart {
  font-family: var(--font-sans); font-weight: 700;
  font-size: 17px; color: var(--ink);
}

main { padding: 16px var(--pad) 8px; max-width: 880px; margin: 0 auto; }

.hero {
  margin: 8px 0 18px;
}
.hero h1 {
  font-family: var(--font-serif); font-style: italic; font-weight: 400;
  font-size: 32px; line-height: 1.1; color: var(--ink);
  margin: 0 0 6px; letter-spacing: -0.015em;
}
.hero h1 strong {
  font-family: var(--font-sans); font-style: normal; font-weight: 700;
  color: var(--accent);
}
.hero .sub {
  font-family: var(--font-mono); font-size: 11px;
  letter-spacing: 0.06em; color: var(--ink-soft);
  text-transform: uppercase;
}

.cam {
  aspect-ratio: 16/9;
  background: #0a1620;
  position: relative; overflow: hidden;
  border-radius: 18px;
  box-shadow:
    0 1px 0 rgba(0,0,0,0.02),
    0 18px 40px -22px rgba(31,63,77,0.5);
  margin-bottom: 12px;
}
.cam iframe { width: 100%; height: 100%; border: 0; display: block; }
.cam-off {
  display: grid; place-items: center; height: 100%;
  color: var(--mute); font-family: var(--font-mono);
  font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase;
}
.cam-tag {
  position: absolute; top: 10px; left: 10px;
  display: inline-flex; align-items: center; gap: 5px;
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.06em; color: white;
  background: rgba(0,0,0,0.55); padding: 4px 8px; border-radius: 999px;
  text-transform: uppercase;
}
.cam-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #ff5b5b;
  animation: live-pulse 2s infinite;
}
@keyframes live-pulse {
  0% { box-shadow: 0 0 0 0 rgba(255,91,91,0.6); }
  70% { box-shadow: 0 0 0 7px rgba(255,91,91,0); }
  100% { box-shadow: 0 0 0 0 rgba(255,91,91,0); }
}
.cam-sub {
  font-family: var(--font-mono); font-size: 11px;
  color: var(--ink-soft); letter-spacing: 0.04em;
  text-transform: lowercase; margin-bottom: 14px;
}

.summary {
  background: var(--card); border: 1px solid var(--line);
  border-radius: 14px; padding: 12px 14px;
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 10px; margin-bottom: 14px;
}
.summary .cell { display: flex; flex-direction: column; gap: 2px; }
.summary .l {
  font-family: var(--font-mono); font-size: 9px;
  letter-spacing: 0.06em; color: var(--mute);
  text-transform: uppercase;
}
.summary .v {
  font-size: 17px; font-weight: 700; color: var(--ink);
  font-variant-numeric: tabular-nums; letter-spacing: -0.01em;
}
.summary .s { font-size: 11px; color: var(--ink-soft); }

.cta {
  display: inline-block; margin: 4px 0 18px;
  padding: 10px 16px; background: var(--accent); color: white;
  border-radius: 999px; font-weight: 700; font-size: 13px;
  letter-spacing: -0.005em;
  box-shadow: 0 8px 20px -10px rgba(232,137,94,0.6);
}
.cta:hover { background: #d77a4f; }

.section-tag {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.08em; color: var(--accent);
  text-transform: uppercase; font-weight: 700;
  margin: 18px 0 8px;
}
"""


_STATUS_LABEL = {
    "propria": "água própria",
    "alerta": "alerta",
    "impropria": "imprópria",
    "sem_dados": "sem boletim",
}


def _load_balne():
    try:
        d = json.load(open(BALNE))
        return d.get("by_beach", {}) if isinstance(d, dict) else {}
    except Exception:
        return {}


def render_page(p, all_postos, balne_by_beach):
    slug = CITY_SLUG_BY_BEACH.get(p["id"])
    if not slug:
        return None  # caller should skip

    yt = p.get("youtube_id")
    beach = p["beach"]
    state = p.get("state", "")
    posto = p.get("posto", "")
    canonical = f"{SITE_URL}/{slug}/webcam-ao-vivo.html"

    if yt:
        cam = (
            f'<iframe src="https://www.youtube.com/embed/{yt}'
            f'?autoplay=1&mute=1&controls=1&modestbranding=1&playsinline=1" '
            'loading="lazy" referrerpolicy="strict-origin-when-cross-origin" '
            'allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>'
        )
    else:
        cam = '<div class="cam-off">câmera ao vivo indisponível</div>'

    w = p.get("weather") or {}
    a = p.get("water") or {}
    temp = fmt(w.get("air_temp_c"), "°", 0)
    wind = fmt(w.get("wind_kmh"), "", 0)
    wd = w.get("wind_dir")
    uv = w.get("uv")
    sea_t = fmt(a.get("sea_temp_c"), "°", 0)

    balne = balne_by_beach.get(p["id"]) or {}
    agua_label = _STATUS_LABEL.get(balne.get("status") or "sem_dados", "sem boletim")

    summary_html = (
        '<div class="summary">'
        f'<div class="cell"><div class="l">ar</div><div class="v">{temp}</div><div class="s">temperatura</div></div>'
        f'<div class="cell"><div class="l">vento</div><div class="v">{wind}<span style="font-size:11px;color:var(--ink-soft)">km/h</span></div>'
        f'<div class="s">{wind_arrow(wd)} {fmt(wd, "°", 0) if wd is not None else "—"}</div></div>'
        f'<div class="cell"><div class="l">uv</div><div class="v">{fmt(uv, "", 0)}</div><div class="s">{uv_label(uv)}</div></div>'
        f'<div class="cell"><div class="l">água</div><div class="v">{sea_t}</div><div class="s">{agua_label}</div></div>'
        '</div>'
    )

    # JSON-LD
    crumb_ld = breadcrumb_jsonld([
        ("Início", f"{SITE_URL}/"),
        (beach, f"{SITE_URL}/{slug}/fim-de-semana.html"),
        ("Câmera ao vivo", canonical),
    ])
    ld_blocks = ['<script type="application/ld+json">'
                 + json.dumps(crumb_ld, ensure_ascii=False) + '</script>']
    if yt:
        video_ld = video_object_jsonld(beach, state, yt, canonical)
        ld_blocks.append('<script type="application/ld+json">'
                         + json.dumps(video_ld, ensure_ascii=False) + '</script>')
    ld_html = "\n".join(ld_blocks)

    page_title = f"Webcam {beach} ao vivo — câmera em tempo real | praia smart"
    page_desc = (
        f"Câmera ao vivo de {beach}, {state or 'Brasil'} — transmissão em tempo real, "
        "ondas, vento, água e movimento da praia. Atualiza automaticamente."
    )
    og_image = (f"https://i.ytimg.com/vi/{yt}/maxresdefault.jpg"
                if yt else f"{SITE_URL}/og-default.jpg")
    seo_html = (
        f'<meta name="description" content="{page_desc}">'
        f'<link rel="canonical" href="{canonical}">'
        f'<meta property="og:type" content="video.other">'
        f'<meta property="og:title" content="{page_title}">'
        f'<meta property="og:description" content="{page_desc}">'
        f'<meta property="og:image" content="{og_image}">'
        f'<meta property="og:url" content="{canonical}">'
        f'<meta property="og:locale" content="pt_BR">'
        f'<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{page_title}">'
        f'<meta name="twitter:description" content="{page_desc}">'
        f'<meta name="twitter:image" content="{og_image}">'
    )

    nearby_html = render_nearby_section(p, all_postos=all_postos, n=3, link_prefix="../beach/")

    analytics_html = ('<script defer data-domain="praiasmart.com" '
                      'src="https://plausible.io/js/script.js"></script>')

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#F4EFE4">
<title>{page_title}</title>
{PRECONNECT_HTML}
{FAVICON_HTML}
{seo_html}
{ld_html}
{analytics_html}
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}{FOOTER_CSS}{NEARBY_CSS}</style>
</head>
<body>
<header class="topbar">
  <a class="back-btn" href="../index.html" aria-label="voltar">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M15 6 L 9 12 L 15 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
  </a>
  <span class="wordmark"><span class="wm-praia">praia</span><span class="wm-smart">smart</span></span>
</header>

<main>
  <section class="hero">
    <h1>Câmera ao vivo — <strong>{beach}</strong>, {state or "Brasil"}</h1>
    <div class="sub">{posto} · transmissão em tempo real</div>
  </section>

  <div class="cam">
    {cam}
    <div class="cam-tag"><span class="cam-dot"></span> ao vivo</div>
  </div>
  <div class="cam-sub">transmissão em tempo real · atualiza automaticamente</div>

  {summary_html}

  <a class="cta" href="../beach/{p['id']}.html">Ver condições completas →</a>

  {nearby_html}

</main>
{FOOTER_HTML}
</body>
</html>"""


def main():
    postos = json.load(open(DATA))
    balne_by_beach = _load_balne()
    written = 0
    for p in postos:
        slug = CITY_SLUG_BY_BEACH.get(p["id"])
        if not slug:
            print(f"  skip {p['id']}: no city slug")
            continue
        html = render_page(p, postos, balne_by_beach)
        if not html:
            continue
        outdir = os.path.join(OUT_ROOT, slug)
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, "webcam-ao-vivo.html")
        open(path, "w").write(html)
        print(f"  wrote {path}")
        written += 1
    print(f"Wrote {written} webcam landing pages")


if __name__ == "__main__":
    main()
