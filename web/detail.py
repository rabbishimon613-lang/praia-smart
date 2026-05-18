"""Per-beach detail page renderer. Reads conditions.json -> web/beach/{id}.html."""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from predictors import predict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "conditions.json")
SHIPS = os.path.join(ROOT, "data", "ships.json")
SATELLITE = os.path.join(ROOT, "data", "satellite.json")
OUTDIR = os.path.join(ROOT, "web", "beach")

WIND_ARROWS = ["↓", "↙", "←", "↖", "↑", "↗", "→", "↘"]


def fmt(v, unit="", nd=1):
    if v is None:
        return "—"
    return f"{v:.{nd}f}{unit}" if isinstance(v, (int, float)) else f"{v}{unit}"


def wind_arrow(deg):
    return "·" if deg is None else WIND_ARROWS[int(((deg + 22.5) % 360) // 45)]


def short_time(iso):
    return datetime.fromisoformat(iso).strftime("%H:%M") if iso else "—"


def cloud_icon(pct, uv):
    if pct is None: return "·"
    if pct < 25: return "☀" if uv and uv > 0 else "🌙"
    if pct < 60: return "⛅"
    if pct < 90: return "☁"
    return "🌧"


def tide_svg(hourly, sunrise_iso, sunset_iso, width=340, height=120):
    """Render a smooth tide curve as inline SVG with day/night shading."""
    times = hourly["time"]
    tides = hourly["tide_m"]
    if not times or not tides:
        return '<div class="empty">sem dados de maré</div>'

    # Normalize
    n = len(tides)
    vals = [t for t in tides if t is not None]
    if not vals:
        return '<div class="empty">sem dados de maré</div>'
    vmin, vmax = min(vals), max(vals)
    span = max(0.1, vmax - vmin)
    pad = 22
    inner_h = height - pad * 2
    inner_w = width - 16

    def x(i): return 8 + i * inner_w / (n - 1)
    def y(v): return pad + (1 - (v - vmin) / span) * inner_h

    # Day shading: hours between sunrise and sunset
    sunrise = short_time(sunrise_iso)
    sunset = short_time(sunset_iso)
    sr_h, sr_m = (int(p) for p in sunrise.split(":")) if ":" in sunrise else (6, 0)
    ss_h, ss_m = (int(p) for p in sunset.split(":")) if ":" in sunset else (18, 0)

    day_rects = []
    for i, t in enumerate(times):
        try:
            h = int(t[11:13])
        except Exception:
            continue
        if (h > sr_h or (h == sr_h and 0 >= sr_m)) and \
           (h < ss_h or (h == ss_h and 0 <= ss_m)):
            x1 = x(i) - (inner_w / (n - 1)) / 2
            x2 = x(i) + (inner_w / (n - 1)) / 2
            day_rects.append(f'<rect x="{x1:.1f}" y="{pad}" width="{x2-x1:.1f}" height="{inner_h}" fill="rgba(255,217,102,0.05)"/>')

    # Curve path
    points = [(x(i), y(t)) for i, t in enumerate(tides) if t is not None]
    path_d = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in points)

    # Now marker (first index = current hour)
    now_x = x(0)

    # High/low dots
    dots = []
    for i in range(1, n - 1):
        if tides[i] is None or tides[i-1] is None or tides[i+1] is None:
            continue
        if tides[i] > tides[i-1] and tides[i] > tides[i+1]:
            dots.append((x(i), y(tides[i]), tides[i], "high"))
        elif tides[i] < tides[i-1] and tides[i] < tides[i+1]:
            dots.append((x(i), y(tides[i]), tides[i], "low"))

    dot_html = ""
    for dx, dy, dv, kind in dots[:4]:
        color = "#5fe0a0" if kind == "high" else "#ffb86b"
        label_y = dy - 6 if kind == "high" else dy + 14
        dot_html += (
            f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="3" fill="{color}"/>'
            f'<text x="{dx:.1f}" y="{label_y:.1f}" text-anchor="middle" '
            f'font-size="10" fill="{color}">{dv:+.1f}m</text>'
        )

    # Hour ticks every 4h
    ticks = ""
    for i in range(0, n, 4):
        try:
            h = times[i][11:13]
            ticks += f'<text x="{x(i):.1f}" y="{height-4}" text-anchor="middle" font-size="9" fill="#7d97b0">{h}h</text>'
        except Exception:
            pass

    return f'''<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" preserveAspectRatio="none">
  {"".join(day_rects)}
  <path d="{path_d}" stroke="#4fc4ff" stroke-width="2" fill="none"/>
  <line x1="{now_x:.1f}" y1="{pad}" x2="{now_x:.1f}" y2="{pad+inner_h}" stroke="#ff7a8a" stroke-dasharray="2,3" stroke-width="1"/>
  <text x="{now_x+3:.1f}" y="{pad+8}" font-size="9" fill="#ff7a8a">agora</text>
  {dot_html}
  {ticks}
</svg>'''


def hourly_strip(hourly, max_h=12):
    """Horizontal scrollable strip of next N hours."""
    out = []
    n = min(max_h, len(hourly["time"]))
    for i in range(n):
        h = hourly["time"][i][11:13]
        temp = fmt(hourly["temp_c"][i], "°", 0)
        wave = fmt(hourly["wave_m"][i], "m", 1)
        wind = fmt(hourly["wind_kmh"][i], "", 0)
        wdir = wind_arrow(hourly["wind_dir"][i])
        ico = cloud_icon(hourly["cloud_pct"][i], hourly["uv"][i])
        out.append(
            f'<div class="h-cell"><span class="h-hr">{h}h</span>'
            f'<span class="h-ico">{ico}</span>'
            f'<span class="h-t">{temp}</span>'
            f'<span class="h-w">{wave}</span>'
            f'<span class="h-wd"><small>{wind} {wdir}</small></span></div>'
        )
    return '<div class="hourly">' + "".join(out) + "</div>"


CSS = """
:root {
  --bg: #0a1620; --card: #14283a; --line: #1f3a52;
  --text: #e7eef5; --muted: #7d97b0; --accent: #4fc4ff;
  --hi: #ffb86b; --lo: #5fe0a0; --warm: #ff9088;
}
* { box-sizing: border-box; }
html, body { margin:0; padding:0; background: var(--bg); color: var(--text);
  font: 15px/1.4 -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased; }
body { padding-bottom: env(safe-area-inset-bottom); }

.nav { position: sticky; top: 0; z-index: 10; background: rgba(10,22,32,0.92);
  backdrop-filter: blur(12px); padding: 12px 14px;
  padding-top: calc(12px + env(safe-area-inset-top));
  border-bottom: 1px solid var(--line); display: flex; gap: 12px; align-items: center; }
.nav a.back { color: var(--accent); text-decoration: none; font-size: 18px;
  padding: 4px 8px; border-radius: 6px; }
.nav a.back:active { background: rgba(79,196,255,0.1); }
.nav h1 { margin: 0; font-size: 16px; font-weight: 700; flex: 1; }
.nav .meta { color: var(--muted); font-size: 12px; }

.hero-cam { aspect-ratio: 16/9; background: #000; }
.hero-cam iframe { width: 100%; height: 100%; border: 0; display: block; }

main { padding: 14px; display: flex; flex-direction: column; gap: 14px; }
section { background: var(--card); border: 1px solid var(--line); border-radius: 12px;
  padding: 14px; }
section h2 { margin: 0 0 10px; font-size: 12px; color: var(--muted);
  text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; }

.now-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.now-cell { display: flex; flex-direction: column; gap: 2px; }
.now-cell .l { font-size: 10px; color: var(--muted); text-transform: uppercase;
  letter-spacing: 0.5px; }
.now-cell .v { font-size: 22px; font-weight: 700; color: var(--accent); }
.now-cell .v small { font-size: 11px; font-weight: 500; color: var(--muted); }
.now-cell .s { font-size: 11px; color: var(--muted); }

.tide-card .extrema { display: flex; justify-content: space-around;
  margin-top: 8px; font-size: 13px; }
.tide-card .extrema .e { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.tide-card .extrema .lbl { font-size: 10px; color: var(--muted); text-transform: uppercase; }
.tide-card .extrema .v { font-size: 16px; font-weight: 700; }
.tide-card .extrema .high .v { color: var(--lo); }
.tide-card .extrema .low .v { color: var(--hi); }

.hourly { display: flex; overflow-x: auto; gap: 4px; padding-bottom: 4px;
  scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch; }
.h-cell { min-width: 58px; padding: 8px 4px; display: flex; flex-direction: column;
  align-items: center; gap: 2px; background: rgba(0,0,0,0.15); border-radius: 8px;
  scroll-snap-align: start; }
.h-hr { font-size: 11px; color: var(--muted); font-weight: 600; }
.h-ico { font-size: 16px; }
.h-t { font-size: 14px; font-weight: 700; }
.h-w { font-size: 11px; color: var(--accent); }
.h-wd { font-size: 10px; color: var(--muted); }

.sun-line { display: flex; justify-content: space-between; align-items: center;
  padding: 6px 0; }
.sun-line .ev { font-size: 14px; }
.sun-line .t { font-size: 16px; font-weight: 700; color: var(--accent); }

.pred-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.pred-cell { padding: 10px 12px; background: rgba(0,0,0,0.18); border-radius: 8px;
  display: flex; flex-direction: column; gap: 4px; }
.pred-cell .ico { font-size: 18px; }
.pred-cell .act { font-size: 11px; color: var(--muted); text-transform: uppercase;
  letter-spacing: 0.5px; font-weight: 600; }
.pred-cell .when { font-size: 16px; font-weight: 700; color: var(--accent);
  margin-top: 2px; }
.pred-cell.empty .when { color: var(--muted); }
.bar { position: relative; background: rgba(255,255,255,0.06); height: 8px;
  border-radius: 4px; margin-top: 8px; overflow: visible; }
.bar-tick { position: absolute; top: 0; bottom: 0; width: 1px;
  background: rgba(255,255,255,0.08); }
.bar-window { position: absolute; top: 0; bottom: 0;
  background: linear-gradient(90deg, var(--lo), var(--accent));
  border-radius: 4px; box-shadow: 0 0 8px rgba(79,196,255,0.4); }
.bar-now { position: absolute; top: -2px; bottom: -2px; width: 2px;
  background: var(--warm); border-radius: 1px; }
.bar-labels { position: absolute; left: 0; right: 0; top: 10px;
  display: flex; justify-content: space-between; font-size: 9px;
  color: var(--muted); pointer-events: none; }
.pred-cell { padding-bottom: 22px; }

.aqi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.aqi-cell { padding: 8px; background: rgba(0,0,0,0.15); border-radius: 8px;
  display: flex; flex-direction: column; gap: 2px; }
.aqi-cell .l { font-size: 10px; color: var(--muted); text-transform: uppercase; }
.aqi-cell .v { font-size: 18px; font-weight: 700; }

.ships-summary { font-size: 12px; color: var(--muted); margin-bottom: 10px; }
.ships-summary small { color: var(--muted); opacity: 0.7; }
.ships-empty { color: var(--muted); font-style: italic; padding: 8px 0; font-size: 13px; }
.ships-list { display: flex; flex-direction: column; gap: 8px; }
.ship { display: flex; gap: 12px; padding: 10px; background: rgba(0,0,0,0.15);
  border-radius: 8px; }
.ship-ico { font-size: 22px; line-height: 1; padding-top: 2px; }
.ship-body { flex: 1; min-width: 0; }
.ship-h { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.ship-name { font-size: 13px; font-weight: 700; color: var(--text); overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap; }
.ship-flag { font-size: 14px; flex-shrink: 0; }
.ship-meta { font-size: 11px; color: var(--accent); margin-top: 2px;
  display: flex; gap: 4px; flex-wrap: wrap; }
.ship-meta span:nth-child(even) { color: var(--muted); }
.ship-status { font-size: 11px; color: var(--muted); margin-top: 2px;
  text-transform: lowercase; }
.ship-dest { font-size: 11px; color: var(--lo); margin-top: 2px; }

.sat-pills { display: flex; gap: 6px; margin-bottom: 10px; overflow-x: auto; }
.sat-pill { background: transparent; color: var(--muted); border: 1px solid var(--line);
  border-radius: 999px; padding: 5px 12px; font: inherit; font-size: 12px;
  font-weight: 600; cursor: pointer; -webkit-tap-highlight-color: transparent; }
.sat-pill.active { background: var(--accent); color: var(--bg); border-color: var(--accent); }
.sat-image { background: #000; border-radius: 8px; overflow: hidden; aspect-ratio: 1/1; }
.sat-image img { width: 100%; height: 100%; object-fit: cover; display: block; }
.sat-cap { font-size: 11px; color: var(--muted); margin-top: 8px; text-align: center; }
.sat-empty { text-align: center; padding: 28px 14px; color: var(--muted); }
.sat-empty-ico { font-size: 36px; margin-bottom: 8px; opacity: 0.6; }
.sat-empty-sub { font-size: 11px; margin-top: 4px; opacity: 0.7; }

.ad-slot { background: rgba(255,255,255,0.03); border: 1px solid var(--line);
  border-radius: 12px; padding: 8px; text-align: center; }
.ad-slot iframe { max-width: 600px; margin: 0 auto; }

.footer { text-align: center; padding: 18px; color: var(--muted); font-size: 11px; }
"""


ACTIVITY_META = {
    "surfar":     {"icon": "🏄", "label": "surfar"},
    "movimento":  {"icon": "👥", "label": "movimento"},
    "pegar_sol":  {"icon": "☀️", "label": "sol forte"},
    "evitar_sol": {"icon": "🧘", "label": "sol tranquilo"},
}


def day_bar(start_iso, end_iso):
    """24h timeline with the activity window highlighted in its real time position."""
    try:
        start_h = datetime.fromisoformat(start_iso).hour
        end_h = (datetime.fromisoformat(end_iso).hour + 1) % 24 or 24
    except Exception:
        return '<div class="bar"></div>'
    left = start_h / 24 * 100
    width = max(4, (end_h - start_h) / 24 * 100)
    now_h = datetime.now().hour
    now_pct = now_h / 24 * 100
    return (
        '<div class="bar">'
        '<span class="bar-tick" style="left:25%"></span>'
        '<span class="bar-tick" style="left:50%"></span>'
        '<span class="bar-tick" style="left:75%"></span>'
        f'<div class="bar-window" style="left:{left:.1f}%;width:{width:.1f}%"></div>'
        f'<div class="bar-now" style="left:{now_pct:.1f}%"></div>'
        '<div class="bar-labels"><span>0h</span><span>6h</span><span>12h</span><span>18h</span><span>24h</span></div>'
        '</div>'
    )


AD_HTML = """
<div class="ad-slot">
  <iframe data-aa='2438112' src='//acceptable.a-ads.com/2438112/?size=Adaptive'
    style='border:0;padding:0;width:100%;height:90px;overflow:hidden;display:block;'></iframe>
</div>
"""


SHIP_ICONS = {
    "cargueiro": "🚢", "petroleiro": "⛽", "cruzeiro": "🛳",
    "passageiros": "⛴", "pesqueiro": "🎣", "rebocador": "🚤",
    "iate": "⛵", "militar": "⚓", "rápido": "💨",
    "draga": "🏗", "outro": "🛥", "—": "🛥",
}


def country_from_mmsi(mmsi):
    """Coarse flag lookup by MID (first 3 digits). Subset; expand as needed."""
    if mmsi is None: return ""
    s = str(mmsi)[:3]
    flags = {
        "710": "🇧🇷", "725": "🇨🇱", "750": "🇪🇨", "775": "🇻🇪", "701": "🇦🇷",
        "303": "🇺🇸", "366": "🇺🇸", "367": "🇺🇸", "338": "🇺🇸",
        "311": "🇧🇸", "319": "🇰🇾", "215": "🇲🇹", "247": "🇮🇹",
        "227": "🇫🇷", "228": "🇫🇷", "211": "🇩🇪", "218": "🇩🇪",
        "636": "🇱🇷", "538": "🇲🇭", "352": "🇵🇦", "355": "🇵🇦",
        "374": "🇵🇦", "477": "🇭🇰", "236": "🇬🇮", "316": "🇨🇦",
        "248": "🇲🇹", "563": "🇸🇬", "564": "🇸🇬",
    }
    return flags.get(s, "")


def load_ships():
    try:
        return json.load(open(SHIPS))
    except Exception:
        return None


def load_satellite():
    try:
        return json.load(open(SATELLITE))
    except Exception:
        return None


def render_satellite(p, sat_data):
    if not sat_data:
        return ""
    records = sat_data.get("by_beach", {}).get(p["id"], [])
    valid = [r for r in records if r.get("status") == "ok"]
    if not valid:
        return '''
  <section>
    <h2>satélite · sentinel-2</h2>
    <div class="sat-empty">
      <div class="sat-empty-ico">☁</div>
      <div>ainda nublado · volte amanhã</div>
      <div class="sat-empty-sub">passa do satélite a cada 5 dias</div>
    </div>
  </section>'''

    # Date label translation
    label_map = {"hoje": "hoje", "3d": "−3d", "7d": "−7d", "14d": "−14d", "30d": "−30d"}

    pills = "".join(
        f'<button class="sat-pill" data-label="{r["label"]}" '
        f'data-img="../{r["image"]}" data-date="{r["date"]}" data-cloud="{r["cloud"]}">'
        f'{label_map.get(r["label"], r["label"])}</button>'
        for r in valid
    )
    first = valid[0]
    return f'''
  <section>
    <h2>satélite · sentinel-2</h2>
    <div class="sat-pills">{pills}</div>
    <div class="sat-image">
      <img id="sat-img" src="../{first["image"]}" alt="satélite">
    </div>
    <div class="sat-cap" id="sat-cap">
      captura {first["date"]} · {first["cloud"]}% nuvens
    </div>
    <script>
    (()=>{{
      const pills = document.querySelectorAll('.sat-pill');
      const img = document.getElementById('sat-img');
      const cap = document.getElementById('sat-cap');
      pills[0].classList.add('active');
      pills.forEach(b => b.addEventListener('click', () => {{
        pills.forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        img.src = b.dataset.img;
        cap.textContent = `captura ${{b.dataset.date}} · ${{b.dataset.cloud}}% nuvens`;
      }}));
    }})();
    </script>
  </section>'''


def render_ships(p, ships_data):
    if not ships_data:
        return ""
    bid = p["id"]
    ships = ships_data.get("by_beach", {}).get(bid, [])
    age_min = (datetime.now().timestamp() - ships_data.get("fetched_at", 0)) / 60

    if not ships:
        return (
            '<section><h2>navios na costa · 50 km</h2>'
            '<div class="ships-empty">horizonte tranquilo · nenhum navio detectado</div>'
            '</section>'
        )

    # Type summary (skip unknown — when all types are "—" we just show the count)
    type_count = {}
    for s in ships:
        t = s.get("type") or "—"
        type_count[t] = type_count.get(t, 0) + 1
    summary_parts = [f"{n} {t}" for t, n in sorted(type_count.items(), key=lambda x: -x[1]) if t != "—"]
    summary = " · ".join(summary_parts) if summary_parts else "tipos desconhecidos"

    items = []
    for s in ships[:12]:
        ico = SHIP_ICONS.get(s.get("type") or "—", "🛥")
        flag = country_from_mmsi(s.get("mmsi"))
        name = s.get("name") or f"MMSI {s.get('mmsi')}"
        ship_type = s.get("type") or "navio"
        dist = s.get("dist_km")
        compass = s.get("compass") or ""
        status = s.get("status") or ""
        speed = s.get("speed_kn")
        speed_txt = f"{speed} nós" if speed and speed > 0.3 else "parado"
        dest = s.get("dest")
        dest_line = f'<div class="ship-dest">→ {dest}</div>' if dest else ""

        items.append(
            f'<div class="ship">'
            f'  <div class="ship-ico">{ico}</div>'
            f'  <div class="ship-body">'
            f'    <div class="ship-h">'
            f'      <span class="ship-name">{name}</span>'
            f'      <span class="ship-flag">{flag}</span>'
            f'    </div>'
            f'    <div class="ship-meta">'
            f'      <span>{ship_type}</span>'
            f'      <span>·</span>'
            f'      <span>{dist} km {compass}</span>'
            f'      <span>·</span>'
            f'      <span>{speed_txt}</span>'
            f'    </div>'
            f'    <div class="ship-status">{status}</div>'
            f'    {dest_line}'
            f'  </div>'
            f'</div>'
        )

    return (
        f'<section><h2>navios na costa · 50 km</h2>'
        f'<div class="ships-summary">{len(ships)} navios · {summary} · '
        f'<small>há {age_min:.0f} min</small></div>'
        f'<div class="ships-list">{"".join(items)}</div>'
        f'</section>'
    )


def render_predictions(p):
    preds = predict(p.get("hourly", {}))
    if not preds:
        return ""
    cells = []
    for key, meta in ACTIVITY_META.items():
        pr = preds.get(key)
        if not pr:
            cells.append(
                f'<div class="pred-cell empty"><span class="ico">{meta["icon"]}</span>'
                f'<span class="act">{meta["label"]}</span>'
                f'<span class="when">—</span></div>'
            )
            continue
        start = short_time(pr["start_time"])
        # end_time is the start of the last hour in the window; show window-end +1h
        end_dt = datetime.fromisoformat(pr["end_time"])
        end = f"{(end_dt.hour + 1) % 24:02d}:00"
        cells.append(
            f'<div class="pred-cell"><span class="ico">{meta["icon"]}</span>'
            f'<span class="act">{meta["label"]}</span>'
            f'<span class="when">{start}–{end}</span>'
            f'{day_bar(pr["start_time"], pr["end_time"])}</div>'
        )
    return f'<section><h2>melhor janela hoje</h2><div class="pred-grid">{"".join(cells)}</div></section>'


def render(p, ships_data=None, sat_data=None):
    yt = p.get("youtube_id")
    cam = (
        f'<iframe src="https://www.youtube.com/embed/{yt}'
        f'?autoplay=1&mute=1&controls=1&modestbranding=1&playsinline=1" '
        'allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>'
        if yt else '<div style="display:grid;place-items:center;height:100%;color:#7d97b0;">imagem indisponível</div>'
    )

    w, s, a, ai, sun = p["weather"], p["surf"], p["water"], p["air"], p["sun"]
    h = p.get("hourly", {})
    nh, nl = a.get("next_high_tide"), a.get("next_low_tide")

    state = (p.get("notes") or "").split("·")[0].strip()
    title_meta = f'{p["posto"]}{" · " + state if state else ""}'

    tide_chart = tide_svg(h, sun["sunrise"], sun["sunset"]) if h.get("time") else ""

    extrema = ""
    if nh:
        extrema += (
            f'<div class="e high"><span class="lbl">próx alta</span>'
            f'<span class="v">{short_time(nh["time"])}</span>'
            f'<span style="font-size:11px;color:var(--muted)">{nh["height_m"]:+.2f}m</span></div>'
        )
    if nl:
        extrema += (
            f'<div class="e low"><span class="lbl">próx baixa</span>'
            f'<span class="v">{short_time(nl["time"])}</span>'
            f'<span style="font-size:11px;color:var(--muted)">{nl["height_m"]:+.2f}m</span></div>'
        )

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0a1620">
<title>{p['beach']} {p['posto']} — praia smart</title>
<style>{CSS}</style>
</head>
<body>
<nav class="nav">
  <a class="back" href="../index.html">←</a>
  <div style="flex:1">
    <h1>{p['beach']}</h1>
    <div class="meta">{title_meta}</div>
  </div>
</nav>
<div class="hero-cam">{cam}</div>
<main>

  <section>
    <h2>agora</h2>
    <div class="now-grid">
      <div class="now-cell"><span class="l">água</span><span class="v">{fmt(a['sea_temp_c'],'°',0)}</span></div>
      <div class="now-cell"><span class="l">ar</span><span class="v">{fmt(w['air_temp_c'],'°',0)}</span></div>
      <div class="now-cell"><span class="l">onda</span><span class="v">{fmt(s['wave_height_m'],'m')}</span><span class="s">{fmt(s['wave_period_s'],'s',0)} período</span></div>
      <div class="now-cell"><span class="l">vento</span><span class="v">{fmt(w['wind_kmh'],'',0)}<small> km/h</small></span><span class="s">{wind_arrow(w['wind_dir'])} {fmt(w['wind_dir'],'°',0)}</span></div>
    </div>
  </section>

  {render_predictions(p)}

  {AD_HTML}

  <section class="tide-card">
    <h2>maré · próximas 24h</h2>
    {tide_chart}
    <div class="extrema">{extrema}</div>
  </section>

  <section>
    <h2>próximas horas</h2>
    {hourly_strip(h)}
  </section>

  <section>
    <h2>sol</h2>
    <div class="sun-line"><span class="ev">☀ nasce</span><span class="t">{short_time(sun['sunrise'])}</span></div>
    <div class="sun-line"><span class="ev">☾ põe</span><span class="t">{short_time(sun['sunset'])}</span></div>
  </section>

  <section>
    <h2>qualidade do ar</h2>
    <div class="aqi-grid">
      <div class="aqi-cell"><span class="l">pm2.5</span><span class="v">{fmt(ai['pm25'],'',0)}</span></div>
      <div class="aqi-cell"><span class="l">pm10</span><span class="v">{fmt(ai['pm10'],'',0)}</span></div>
      <div class="aqi-cell"><span class="l">aqi</span><span class="v">{fmt(ai['aqi'],'',0)}</span></div>
    </div>
  </section>

  {AD_HTML}

  {render_ships(p, ships_data)}

  {render_satellite(p, sat_data)}

</main>
<div class="footer">dados Open-Meteo · cam YouTube</div>
</body>
</html>"""


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    postos = json.load(open(DATA))
    ships_data = load_ships()
    sat_data = load_satellite()
    for p in postos:
        path = os.path.join(OUTDIR, f"{p['id']}.html")
        open(path, "w").write(render(p, ships_data, sat_data))
    print(f"Wrote {len(postos)} detail pages to {OUTDIR}")


if __name__ == "__main__":
    main()
