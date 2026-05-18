"""Generate web/index.html from data/conditions.json.

Mobile-first. Leads with cross-posto winners ("qual praia pra X agora"),
sorts cards by surf score, badges/highlights notable values.
"""
import json
import math
import os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "conditions.json")
ALERTS = os.path.join(ROOT, "data", "alerts.json")
NEWS = os.path.join(ROOT, "data", "news.json")
AGITO = os.path.join(ROOT, "data", "agito.json")
OUT = os.path.join(ROOT, "web", "index.html")

BUCKET_CLASS = {"vazia": "v", "moderada": "m", "cheia": "c", "lotada": "l"}

AD_HTML = """
<div class="ad-slot">
  <iframe data-aa='2438112' src='//acceptable.a-ads.com/2438112/?size=Adaptive'
    style='border:0;padding:0;width:100%;height:90px;overflow:hidden;display:block;'></iframe>
</div>
"""


def insert_ads(cards, after_positions=(2, 7, 12, 17, 22)):
    """Insert AD_HTML after the given 1-based card positions."""
    out = []
    for i, card in enumerate(cards):
        out.append(card)
        if (i + 1) in after_positions:
            out.append(AD_HTML)
    return "\n".join(out)


def load_optional(path):
    try:
        return json.load(open(path))
    except Exception:
        return None

WIND_ARROWS = ["↓", "↙", "←", "↖", "↑", "↗", "→", "↘"]


def wind_arrow(deg):
    if deg is None:
        return "·"
    return WIND_ARROWS[int(((deg + 22.5) % 360) // 45)]


def offshore_component(wind_dir):
    """Rio south-facing beaches: wind FROM north is offshore. +1 N, -1 S."""
    if wind_dir is None:
        return 0
    return math.cos(math.radians(wind_dir))


def surf_score(p):
    s, w = p["surf"], p["weather"]
    h = s.get("wave_height_m") or 0
    period = s.get("wave_period_s") or 0
    wind = w.get("wind_kmh") or 0
    # Bell curve around 1.5m, zero outside 0.4-3.0m
    if h < 0.4 or h > 3.0:
        size = 0
    else:
        size = max(0.0, 1 - abs(h - 1.5) / 1.5)
    period_score = min(period / 14, 1.0)  # 14s = peak
    offshore = max(0, offshore_component(w.get("wind_dir"))) * min(wind / 15, 1.0)
    return round(size * 0.5 + period_score * 0.3 + offshore * 0.2, 3)


def swim_score(p):
    s, a = p["surf"], p["water"]
    h = s.get("wave_height_m") or 0
    temp = a.get("sea_temp_c") or 0
    calm = 1 / (1 + h)  # smaller wave = higher
    warmth = max(0, min((temp - 18) / 12, 1.0))  # 18-30 range
    return round(calm * 0.6 + warmth * 0.4, 3)


def sun_score(p):
    w = p["weather"]
    cloud = w.get("cloud_pct") or 0
    uv = w.get("uv") or 0
    wind = w.get("wind_kmh") or 0
    clear = (100 - cloud) / 100
    uv_score = uv / 8 if uv <= 8 else max(0, 1 - (uv - 8) / 4)
    breeze = max(0, 1 - wind / 30)
    return round(clear * 0.5 + uv_score * 0.3 + breeze * 0.2, 3)


def fmt(v, unit="", nd=1):
    if v is None:
        return "—"
    if isinstance(v, (int, float)):
        return f"{v:.{nd}f}{unit}"
    return f"{v}{unit}"


def time_short(iso):
    if not iso:
        return "—"
    try:
        return datetime.fromisoformat(iso).strftime("%H:%M")
    except Exception:
        return iso


def aqi_label(aqi):
    if aqi is None:
        return ("—", "muted")
    if aqi <= 20: return ("ar bom", "good")
    if aqi <= 40: return ("ar ok", "ok")
    if aqi <= 60: return ("ar moderado", "warn")
    return ("ar ruim", "bad")


def render_movimento_stat(p, agito_data):
    info = (agito_data or {}).get("by_beach", {}).get(p["id"]) if agito_data else None
    if not info:
        return ('<div class="stat"><span class="lbl">movimento</span>'
                '<span class="val muted">—</span></div>')
    cur = info["current"]
    cls = BUCKET_CLASS.get(cur["bucket"], "m")
    return (
        f'<div class="stat"><span class="lbl">movimento</span>'
        f'<span class="val mv mv-{cls}">{cur["bucket"]}</span></div>'
    )


def render_card(p, marks, agito_data=None):
    yt = p.get("youtube_id")
    if yt:
        media = (
            f'<iframe src="https://www.youtube.com/embed/{yt}'
            f'?autoplay=1&mute=1&controls=0&modestbranding=1&playsinline=1" '
            'allow="autoplay; encrypted-media; picture-in-picture" '
            'allowfullscreen loading="lazy"></iframe>'
        )
    else:
        media = '<div class="no-cam">imagem indisponível</div>'

    w, s, a = p["weather"], p["surf"], p["water"]

    badges = []
    if marks.get("surf") == p["id"]:
        badges.append('<span class="badge surf">🏄 melhor onda</span>')
    if marks.get("swim") == p["id"]:
        badges.append('<span class="badge swim">🏊 mais calma</span>')
    if marks.get("warmest") == p["id"]:
        badges.append('<span class="badge warm">🌡 água quente</span>')
    badges_html = "".join(badges)

    def cls(metric, val):
        if val is None: return ""
        if marks.get(f"max_{metric}") == p["id"]: return " hi"
        if marks.get(f"min_{metric}") == p["id"]: return " lo"
        return ""

    nh, nl = a.get("next_high_tide"), a.get("next_low_tide")
    tide_parts = []
    if nh: tide_parts.append(f"↑ {time_short(nh['time'])} <small>{nh['height_m']:+.1f}m</small>")
    if nl: tide_parts.append(f"↓ {time_short(nl['time'])} <small>{nl['height_m']:+.1f}m</small>")
    tide_row = (
        f'<div class="tide"><span class="lbl">maré</span><span>{" · ".join(tide_parts)}</span></div>'
        if tide_parts else ""
    )

    return f"""
<article class="card" data-state="{p.get('state','?')}" data-surf="{p['_surf']}" data-swim="{p['_swim']}" data-sun="{p['_sun']}">
  <a class="card-link" href="beach/{p['id']}.html">
  <header class="card-h">
    <h2>{p['beach']} <span class="posto">{p['posto']}</span></h2>
    <div class="badges">{badges_html}</div>
  </header>
  </a>
  <div class="media">{media}</div>
  <div class="stats">
    <div class="stat">
      <span class="lbl">onda</span>
      <span class="val{cls('wave', s.get('wave_height_m'))}">{fmt(s.get('wave_height_m'), 'm')}</span>
      <span class="sub">{fmt(s.get('wave_period_s'), 's', 0)} período</span>
    </div>
    <div class="stat">
      <span class="lbl">água</span>
      <span class="val{cls('seatemp', a.get('sea_temp_c'))}">{fmt(a.get('sea_temp_c'), '°', 0)}</span>
    </div>
    <div class="stat">
      <span class="lbl">vento</span>
      <span class="val{cls('wind', w.get('wind_kmh'))}">{fmt(w.get('wind_kmh'), '', 0)}<small> km/h</small></span>
      <span class="sub">{wind_arrow(w.get('wind_dir'))} {fmt(w.get('wind_dir'), '°', 0)}</span>
    </div>
    {render_movimento_stat(p, agito_data)}
  </div>
  <a class="card-link" href="beach/{p['id']}.html">{tide_row}<div class="card-cta">ver detalhes →</div></a>
</article>
"""


CSS = """
:root {
  --bg: #0a1620; --card: #14283a; --line: #1f3a52;
  --text: #e7eef5; --muted: #7d97b0;
  --accent: #4fc4ff; --hi: #ffb86b; --lo: #5fe0a0;
  --surf: #ffb86b; --swim: #5fe0a0; --sun: #ffd966; --warm: #ff9088;
  --good: #5fe0a0; --ok: #8bd9d3; --warn: #ffc14d; --bad: #ff7a8a;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text);
  font: 15px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased; }
body { padding-bottom: env(safe-area-inset-bottom); }

.topbar { position: sticky; top: 0; z-index: 10; background: rgba(10,22,32,0.94);
  backdrop-filter: blur(12px); padding: 12px 16px 10px;
  padding-top: calc(12px + env(safe-area-inset-top));
  border-bottom: 1px solid var(--line); }
.topbar h1 { margin: 0; font-size: 18px; font-weight: 700; }
.topbar h1 .em { color: var(--accent); }
.topbar .sub { color: var(--muted); font-size: 12px; margin-top: 4px; }

.pills { display: flex; gap: 6px; margin-top: 10px; overflow-x: auto;
  -webkit-overflow-scrolling: touch; padding-bottom: 2px; }
.pills::-webkit-scrollbar { display: none; }
.pill { flex: 0 0 auto; background: transparent; color: var(--muted);
  border: 1px solid var(--line); border-radius: 999px; padding: 5px 12px;
  font: inherit; font-size: 12px; font-weight: 600; letter-spacing: 0.3px;
  cursor: pointer; -webkit-tap-highlight-color: transparent;
  transition: all 0.15s; }
.pill:hover { color: var(--text); border-color: var(--muted); }
.pill.active { background: var(--accent); color: var(--bg); border-color: var(--accent); }
.pill.nav { text-decoration: none; color: var(--text); border-color: transparent;
  background: rgba(255,255,255,0.04); }
.pill.nav:hover, .pill.nav:active { background: rgba(79,196,255,0.15); color: var(--accent); }
.pill.nav-first { margin-left: auto; }

.hero { padding: 14px 12px 4px; }
.hero-grid { display: grid; grid-template-columns: 1fr; gap: 8px; }
@media (min-width: 600px) { .hero-grid { grid-template-columns: repeat(3, 1fr); gap: 10px; } }
.hero-card { background: var(--card); border: 1px solid var(--line); border-radius: 12px;
  padding: 12px 14px; display: flex; flex-direction: column; gap: 2px;
  border-left: 3px solid var(--accent);
  text-decoration: none; color: inherit; -webkit-tap-highlight-color: transparent; }
.hero-card:active { transform: scale(0.98); }
.hero-card.surf { border-left-color: var(--surf); }
.hero-card.swim { border-left-color: var(--swim); }
.hero-card.sun { border-left-color: var(--sun); }
.hero-card .ico { font-size: 18px; }
.hero-card .h { font-size: 11px; color: var(--muted); text-transform: uppercase;
  letter-spacing: 0.5px; font-weight: 600; }
.hero-card .name { font-size: 17px; font-weight: 700; margin-top: 2px; }
.hero-card .why { font-size: 12px; color: var(--muted); margin-top: 2px; }

main { padding: 12px; display: grid; gap: 14px; grid-template-columns: 1fr; }
@media (min-width: 720px) { main { grid-template-columns: repeat(2, 1fr); padding: 16px; gap: 16px; } }
@media (min-width: 1100px) { main { grid-template-columns: repeat(3, 1fr); max-width: 1400px; margin: 0 auto; } }

.card { background: var(--card); border: 1px solid var(--line); border-radius: 14px;
  overflow: hidden; display: flex; flex-direction: column; }
.card-h { display: flex; justify-content: space-between; align-items: center;
  gap: 8px; padding: 12px 14px 8px; }
.card-h h2 { margin: 0; font-size: 16px; font-weight: 700; }
.card-h .posto { color: var(--muted); font-weight: 500; margin-left: 4px; font-size: 14px; }
.badges { display: flex; gap: 4px; flex-wrap: wrap; justify-content: flex-end; }
.badge { font-size: 10px; padding: 3px 7px; border-radius: 999px; font-weight: 600;
  white-space: nowrap; }
.badge.surf { background: rgba(255,184,107,0.18); color: var(--surf); }
.badge.swim { background: rgba(95,224,160,0.18); color: var(--swim); }
.badge.warm { background: rgba(255,144,136,0.18); color: var(--warm); }

.media { aspect-ratio: 16/9; background: #000; position: relative; }
.media iframe { width: 100%; height: 100%; border: 0; display: block; }
.no-cam { position: absolute; inset: 0; display: grid; place-items: center;
  color: var(--muted); font-size: 13px; background: linear-gradient(135deg, #1a2f44, #0f2030); }

.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px;
  background: var(--line); border-top: 1px solid var(--line); }
.stat { background: var(--card); padding: 10px 12px; display: flex; flex-direction: column;
  align-items: flex-start; gap: 2px; min-height: 70px; }
.stat .lbl { font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
.stat .val { font-size: 20px; font-weight: 700; line-height: 1.1; }
.stat .val small { font-size: 11px; font-weight: 500; color: var(--muted); }
.stat .val.hi { color: var(--hi); }
.stat .val.lo { color: var(--lo); }
.stat .val.muted { color: var(--muted); font-weight: 500; }
.stat .val.mv { font-size: 14px; padding: 3px 9px; border-radius: 999px;
  font-weight: 700; text-transform: lowercase; letter-spacing: 0.2px;
  display: inline-block; line-height: 1.4; align-self: flex-start; }
.stat .val.mv-v { background: rgba(95,224,160,0.18); color: var(--good); }
.stat .val.mv-m { background: rgba(139,217,211,0.18); color: var(--ok); }
.stat .val.mv-c { background: rgba(255,193,77,0.18); color: var(--warn); }
.stat .val.mv-l { background: rgba(255,122,138,0.18); color: var(--bad); }

.ad-slot { background: rgba(255,255,255,0.03); border: 1px solid var(--line);
  border-radius: 12px; padding: 8px; text-align: center;
  grid-column: 1 / -1; }
.ad-slot iframe { max-width: 600px; margin: 0 auto; }
.stat .sub { font-size: 11px; color: var(--muted); }

.card-link { color: inherit; text-decoration: none; display: block;
  -webkit-tap-highlight-color: transparent; }
.card-link:active { background: rgba(79,196,255,0.04); }
.card-cta { padding: 8px 14px 12px; font-size: 11px; color: var(--accent);
  font-weight: 600; letter-spacing: 0.3px; }

.tide { padding: 9px 14px; font-size: 12px; color: var(--text);
  display: flex; gap: 10px; align-items: center; border-top: 1px solid var(--line); }
.tide .lbl { font-size: 10px; color: var(--muted); text-transform: uppercase;
  letter-spacing: 0.5px; font-weight: 600; }
.tide small { color: var(--muted); margin-left: 2px; }

.alert-banner { background: rgba(255,122,138,0.12);
  border-bottom: 1px solid rgba(255,122,138,0.3);
  padding: 10px 16px; font-size: 13px; color: var(--bad);
  display: flex; gap: 8px; align-items: center; }
.alert-banner .ev { color: var(--text); font-weight: 600; }
.alert-banner .area { color: var(--muted); font-size: 11px; }

.footer { text-align: center; padding: 24px 16px; color: var(--muted); font-size: 11px; }
"""


def main():
    postos = json.load(open(DATA))
    for p in postos:
        p["_surf"] = surf_score(p)
        p["_swim"] = swim_score(p)
        p["_sun"] = sun_score(p)

    def top(key):
        return max(postos, key=lambda p: p[key])

    surf_w, swim_w, sun_w = top("_surf"), top("_swim"), top("_sun")
    warmest = max(postos, key=lambda p: p["water"]["sea_temp_c"] or 0)

    def argmax(metric_path):
        valid = [p for p in postos if _get(p, metric_path) is not None]
        return max(valid, key=lambda p: _get(p, metric_path))["id"] if valid else None

    def argmin(metric_path):
        valid = [p for p in postos if _get(p, metric_path) is not None]
        return min(valid, key=lambda p: _get(p, metric_path))["id"] if valid else None

    marks = {
        "surf": surf_w["id"],
        "swim": swim_w["id"],
        "sun": sun_w["id"],
        "warmest": warmest["id"],
        "max_wave": argmax("surf.wave_height_m"),
        "min_wave": argmin("surf.wave_height_m"),
        "max_seatemp": argmax("water.sea_temp_c"),
        "max_wind": argmax("weather.wind_kmh"),
        "min_wind": argmin("weather.wind_kmh"),
    }

    # Sort by surf score (default mode)
    postos_sorted = sorted(postos, key=lambda p: -p["_surf"])
    agito_data = load_optional(AGITO)
    card_list = [render_card(p, marks, agito_data) for p in postos_sorted]
    cards = insert_ads(card_list)

    ts = datetime.fromtimestamp(postos[0]["fetched_at"]).strftime("%H:%M")
    sample = postos[0]
    aqi_text, aqi_class = aqi_label(sample["air"]["aqi"])
    uv_avg = round(sum(p["weather"]["uv"] or 0 for p in postos) / len(postos), 1)
    cloud_avg = round(sum(p["weather"]["cloud_pct"] or 0 for p in postos) / len(postos))
    region_count = len({p["beach"] for p in postos})
    region_label = "Brasil" if region_count > 1 else postos[0]["beach"].split()[0]

    # Alerts banner
    alerts_data = load_optional(ALERTS) or {}
    active_alerts = alerts_data.get("alerts", [])
    alert_banner = ""
    if active_alerts:
        a = active_alerts[0]
        more = f' · +{len(active_alerts)-1}' if len(active_alerts) > 1 else ""
        alert_banner = (
            f'<div class="alert-banner">⚠️ '
            f'<span class="ev">{a.get("event") or a.get("title")}</span>'
            f'<span class="area">{a.get("severity","").upper()}{more}</span></div>'
        )

    def why_surf(p):
        return f"onda {fmt(p['surf']['wave_height_m'], 'm')} · {fmt(p['surf']['wave_period_s'], 's', 0)} período"

    def why_swim(p):
        return f"onda {fmt(p['surf']['wave_height_m'], 'm')} · água {fmt(p['water']['sea_temp_c'], '°', 0)}"

    def why_sun(p):
        return f"nuvens {fmt(p['weather']['cloud_pct'], '%', 0)} · uv {fmt(p['weather']['uv'], '', 0)}"

    states = sorted({p["state"] for p in postos if p.get("state")})
    state_pills = (
        '<button class="pill active" data-st="all">todas</button>'
        + "".join(f'<button class="pill" data-st="{s}">{s}</button>' for s in states)
        + '<a class="pill nav nav-first" href="melhores.html">melhores</a>'
        + '<a class="pill nav" href="sobre.html">sobre</a>'
    )

    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0a1620">
<title>praia smart — {region_label} agora</title>
<style>{CSS}</style>
</head>
<body>
<header class="topbar">
  <h1>praia <span class="em">smart</span></h1>
  <div class="sub">{region_label} · atualizado {ts} · {aqi_text} · uv {uv_avg} · nuvens {cloud_avg}%</div>
  <div class="pills">{state_pills}</div>
</header>
{alert_banner}
<main id="grid">
{cards}
</main>
<div class="footer">dados Open-Meteo · câmeras YouTube · v0.3</div>
<script>
(()=>{{
  const pills = document.querySelectorAll('.pill');
  pills.forEach(b => b.addEventListener('click', () => {{
    pills.forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    const st = b.dataset.st;
    document.querySelectorAll('.card').forEach(c => {{
      c.style.display = (st === 'all' || c.dataset.state === st) ? '' : 'none';
    }});
  }}));
}})();
</script>
</body>
</html>"""
    open(OUT, "w").write(html)
    print(f"Wrote {OUT}")
    print(f"Surf: {surf_w['beach']} {surf_w['posto']} ({surf_w['_surf']})")
    print(f"Swim: {swim_w['beach']} {swim_w['posto']} ({swim_w['_swim']})")
    print(f"Sun:  {sun_w['beach']} {sun_w['posto']} ({sun_w['_sun']})")


def _get(d, path):
    for k in path.split("."):
        d = d.get(k) if isinstance(d, dict) else None
        if d is None: return None
    return d


if __name__ == "__main__":
    main()
