"""Per-beach detail page renderer. Reads conditions.json -> web/beach/{id}.html.

Light "praia 10am" redesign — shares tokens and primitives with build.py.
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from predictors import predict
from build import (
    surf_score, swim_score, sun_score, shade_score, hourly_scores,
    render_sun_arc, render_hourly_strip, render_crowd_meter,
    render_best_window, render_activity_glyph, best_window,
    wind_arrow, fmt, time_short, uv_label, _icon, aqi_label,
    ACTIVITY_LABEL, ACTIVITY_VAR, BUCKET_INDEX,
    CATEGORIES, pick_top_dials, render_category_glyph,
    render_agua_box, _BALNE_BY_BEACH,
    AD_HTML,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "conditions.json")
SHIPS = os.path.join(ROOT, "data", "ships.json")
SATELLITE = os.path.join(ROOT, "data", "satellite.json")
AGITO = os.path.join(ROOT, "data", "agito.json")
OUTDIR = os.path.join(ROOT, "web", "beach")


def tide_svg(hourly, sunrise_iso, sunset_iso, width=340, height=110):
    """Smooth tide curve as inline SVG, light theme."""
    times = hourly.get("time") or []
    tides = hourly.get("tide_m") or []
    if not times or not tides:
        return '<div class="empty">sem dados de maré</div>'

    n = len(tides)
    vals = [t for t in tides if t is not None]
    if not vals:
        return '<div class="empty">sem dados de maré</div>'
    vmin, vmax = min(vals), max(vals)
    span = max(0.1, vmax - vmin)
    pad = 18
    inner_h = height - pad * 2
    inner_w = width - 16

    def x(i): return 8 + i * inner_w / max(1, n - 1)
    def y(v): return pad + (1 - (v - vmin) / span) * inner_h

    sr = time_short(sunrise_iso); ss = time_short(sunset_iso)
    sr_h = int(sr.split(":")[0]) if ":" in sr else 6
    ss_h = int(ss.split(":")[0]) if ":" in ss else 18

    day_rects = []
    for i, t in enumerate(times):
        try:
            h = int(t[11:13])
        except Exception:
            continue
        if sr_h <= h <= ss_h:
            w = inner_w / max(1, n - 1)
            x1 = x(i) - w / 2
            day_rects.append(
                f'<rect x="{x1:.1f}" y="{pad}" width="{w:.1f}" height="{inner_h}" '
                f'fill="rgba(229,184,106,0.10)"/>'
            )

    points = [(x(i), y(t)) for i, t in enumerate(tides) if t is not None]
    path_d = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in points)
    area_d = path_d + f" L {points[-1][0]:.1f} {pad + inner_h} L {points[0][0]:.1f} {pad + inner_h} Z"

    now_x = x(0)

    dots = []
    for i in range(1, n - 1):
        if tides[i] is None or tides[i - 1] is None or tides[i + 1] is None:
            continue
        if tides[i] > tides[i - 1] and tides[i] > tides[i + 1]:
            dots.append((x(i), y(tides[i]), tides[i], "high"))
        elif tides[i] < tides[i - 1] and tides[i] < tides[i + 1]:
            dots.append((x(i), y(tides[i]), tides[i], "low"))

    dot_html = ""
    for dx, dy, dv, kind in dots[:4]:
        color = "var(--swim)" if kind == "high" else "var(--sun)"
        label_y = dy - 6 if kind == "high" else dy + 14
        dot_html += (
            f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="3.5" fill="{color}"/>'
            f'<text x="{dx:.1f}" y="{label_y:.1f}" text-anchor="middle" '
            f'font-family="JetBrains Mono, monospace" font-size="9" fill="{color}">{dv:+.1f}m</text>'
        )

    ticks = ""
    for i in range(0, n, 6):
        try:
            h = times[i][11:13]
            ticks += (f'<text x="{x(i):.1f}" y="{height - 3}" text-anchor="middle" '
                      f'font-family="JetBrains Mono, monospace" font-size="9" '
                      f'fill="var(--mute)">{h}h</text>')
        except Exception:
            pass

    return f'''<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" preserveAspectRatio="none" style="display:block">
  <defs>
    <linearGradient id="tide-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="var(--swim)" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="var(--swim)" stop-opacity="0"/>
    </linearGradient>
  </defs>
  {"".join(day_rects)}
  <path d="{area_d}" fill="url(#tide-grad)"/>
  <path d="{path_d}" stroke="var(--swim)" stroke-width="2" fill="none" stroke-linecap="round"/>
  <line x1="{now_x:.1f}" y1="{pad}" x2="{now_x:.1f}" y2="{pad+inner_h}" stroke="var(--ink)" stroke-width="1" stroke-dasharray="2,3" opacity="0.45"/>
  <text x="{now_x+3:.1f}" y="{pad+8}" font-family="JetBrains Mono, monospace" font-size="9" fill="var(--accent)" font-weight="700">agora</text>
  {dot_html}
  {ticks}
</svg>'''


def load_optional(path):
    try:
        return json.load(open(path))
    except Exception:
        return None


CSS = """
:root {
  --paper:#F4EFE4; --paper-warm:#F9F4E8; --card:#FFFFFF;
  --ink:#1F3F4D; --ink-soft:#577485; --mute:#94A8B4;
  --line:#E6DCC8; --track:#EADFC8; --track-tick:#D2C2A2;
  --sea:#2D5566;
  --surf:#E8895E; --swim:#5A9FB5; --sun:#E5B86A; --shade:#7C9183;
  --accent:#E8895E;
  --good:#5BB48A; --ok:#5A9FB5; --warn:#E5B86A; --bad:#D44A2A;
  --font-sans:"Plus Jakarta Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
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
  color: var(--ink);
  font-family: var(--font-sans);
  font-size: 15px; line-height: 1.4;
  -webkit-font-smoothing: antialiased;
}
body { padding-bottom: env(safe-area-inset-bottom); }
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
.topbar-title { min-width: 0; flex: 1; }
.topbar-title h1 {
  margin: 0; font-size: 18px; font-weight: 700;
  letter-spacing: -0.015em; color: var(--ink);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.topbar-meta {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.06em; color: var(--ink-soft);
  text-transform: uppercase; margin-top: 2px;
}

.cam {
  aspect-ratio: 16/9;
  background: #0a1620;
  position: relative; overflow: hidden;
  margin: 12px var(--pad) 0;
  border-radius: 18px;
  box-shadow:
    0 1px 0 rgba(0,0,0,0.02),
    0 16px 36px -22px rgba(31,63,77,0.45);
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

main { padding: 14px var(--pad); display: flex; flex-direction: column; gap: 14px; max-width: 720px; margin: 0 auto; }
section {
  background: var(--card); border-radius: 18px;
  padding: 14px 16px;
  box-shadow:
    0 1px 0 rgba(0,0,0,0.02),
    0 12px 30px -22px rgba(31,63,77,0.35),
    inset 0 0 0 1px rgba(230,220,200,0.6);
}
.section-tag {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.08em; color: var(--accent);
  text-transform: uppercase; font-weight: 700;
  margin-bottom: 10px;
}
.section-tag .sub { color: var(--mute); margin-left: 6px; font-weight: 500; }

/* Água box */
.agua-box {
  position: relative;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 14px 14px 14px 18px;
  margin-bottom: 14px;
  display: flex; flex-direction: column; gap: 4px;
}
.agua-box::before {
  content: ""; position: absolute;
  left: 0; top: 10px; bottom: 10px; width: 4px;
  background: var(--agua-c, var(--mute));
  border-radius: 4px;
}
.agua-status {
  font-weight: 800; font-size: 26px; line-height: 1.1;
  letter-spacing: -0.015em;
}
.agua-meta {
  font-family: var(--font-mono); font-size: 11px;
  color: var(--ink-soft); letter-spacing: 0.02em;
}
.agua-rain {
  margin-top: 6px;
  font-size: 12px; color: var(--bad); font-weight: 600;
  display: flex; gap: 6px; align-items: center;
}
.agua-rain-icon { font-size: 14px; }
.agua-ecoli {
  font-family: var(--font-mono); font-size: 13px;
  color: var(--ink); margin-top: 6px;
}
.agua-link {
  font-size: 13px; color: var(--accent); font-weight: 600;
  text-decoration: none; margin-top: 6px; display: inline-block;
}
.agua-link:hover { text-decoration: underline; }
.agua-explainer {
  font-size: 11px; color: var(--mute); margin-top: 8px;
  font-style: italic; line-height: 1.4;
}

/* Score row (sun-arc) — copied from build.py */
.score-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; padding: 4px 0 0; }
.sa { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.sa-label {
  font-size: 11px; font-weight: 600;
  color: var(--ink-soft); letter-spacing: -0.005em; text-align: center;
}

/* Hourly strip */
.hs {
  display: flex; flex-direction: column; gap: 6px;
  padding: 4px 0;
}
.hs-axis {
  display: flex; justify-content: space-between;
  padding: 0 60px 4px 80px;
  font-family: var(--font-mono); font-size: 9px;
  letter-spacing: 0.06em; color: var(--mute); text-transform: uppercase;
}
.hs-row { display: grid; grid-template-columns: 76px 1fr 50px; align-items: center; gap: 6px; }
.hs-label { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 600; color: var(--ink-soft); }
.hs-bars { position: relative; display: grid; grid-template-columns: repeat(24, 1fr); align-items: flex-end; gap: 1px; height: 26px; padding-bottom: 2px; }
.hs-bar { height: var(--h, 2px); background: color-mix(in oklab, var(--c, var(--ink-soft)) 35%, transparent); border-radius: 1.5px; align-self: end; }
.hs-bar.in-win { background: var(--c, var(--ink-soft)); }
.hs-bar.is-now { background: var(--c, var(--ink-soft)); box-shadow: 0 0 0 1.5px rgba(31,63,77,0.18); position: relative; z-index: 1; }
.hs-now-line { position: absolute; top: -2px; bottom: 0; width: 1.5px; background: var(--ink); transform: translateX(-50%); opacity: 0.5; }
.hs-window-underline { position: absolute; bottom: -3px; height: 2px; border-radius: 1px; opacity: 0.7; }
.hs-window-label { font-family: var(--font-mono); font-size: 10px; font-weight: 600; letter-spacing: 0.02em; text-align: right; font-variant-numeric: tabular-nums; }

/* Best window */
.bw {
  position: relative;
  display: grid; grid-template-columns: auto 1fr auto;
  gap: 10px; align-items: center;
  padding: 10px 12px;
  background: color-mix(in oklab, var(--bw-c, var(--accent)) 8%, var(--paper-warm));
  border-radius: 12px;
}
.bw-bar { width: 3px; min-height: 22px; background: var(--bw-c, var(--accent)); border-radius: 2px; align-self: stretch; }
.bw-text { font-size: 13px; color: var(--ink); font-weight: 500; }
.bw-window {
  font-family: var(--font-mono); font-size: 11px;
  letter-spacing: 0.04em; color: var(--bw-c, var(--accent));
  background: var(--card); padding: 4px 8px;
  border-radius: 999px; font-weight: 600; white-space: nowrap;
}

/* Conditions */
.cond { display: grid; grid-template-columns: repeat(4, 1fr); }
.cond-i {
  display: flex; flex-direction: column; gap: 2px;
  padding: 0 4px;
  border-right: 1px dashed rgba(230,220,200,0.7);
}
.cond-i:last-child { border-right: none; }
.cond-i:first-child { padding-left: 0; }
.cond-ico { color: var(--ink-soft); margin-bottom: 2px; }
.cond-v {
  font-weight: 700; font-size: 17px;
  color: var(--ink); line-height: 1.05;
  letter-spacing: -0.015em;
  font-variant-numeric: tabular-nums;
}
.cond-v small { font-weight: 500; font-size: 10px; color: var(--ink-soft); margin-left: 1px; }
.cond-l { font-size: 10px; font-weight: 500; color: var(--ink-soft); letter-spacing: 0.02em; }

/* Extra stats */
.detail-extra {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 6px; margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed rgba(230,220,200,0.85);
}
.extra { display: flex; flex-direction: column; gap: 1px; }
.extra-l { font-family: var(--font-mono); font-size: 9px; letter-spacing: 0.06em; color: var(--mute); text-transform: uppercase; }
.extra-v { font-size: 14px; font-weight: 700; color: var(--ink); font-variant-numeric: tabular-nums; }

/* Tide extrema */
.tide-meta { display: flex; gap: 14px; justify-content: flex-end; margin-bottom: 4px; }
.tide-meta-i { display: inline-flex; align-items: baseline; gap: 4px; font-family: var(--font-mono); font-size: 11px; color: var(--ink-soft); }
.tide-meta-i .arr { font-size: 13px; }
.tide-meta-i .arr.up { color: var(--swim); }
.tide-meta-i .arr.dn { color: var(--sun); }
.tide-meta-i .t { color: var(--ink); font-weight: 700; }
.empty { color: var(--mute); font-style: italic; padding: 14px 0; font-size: 13px; }

/* Hourly cells */
.hourly { display: flex; overflow-x: auto; gap: 6px; padding-bottom: 4px; -webkit-overflow-scrolling: touch; scrollbar-width: none; }
.hourly::-webkit-scrollbar { display: none; }
.h-cell {
  min-width: 58px; padding: 8px 6px;
  display: flex; flex-direction: column; align-items: center; gap: 3px;
  background: var(--paper-warm); border-radius: 12px;
  border: 1px solid var(--line);
}
.h-cell.is-now { background: color-mix(in oklab, var(--accent) 14%, var(--paper-warm)); border-color: var(--accent); }
.h-hr { font-family: var(--font-mono); font-size: 10px; color: var(--mute); letter-spacing: 0.04em; font-weight: 600; }
.h-ico { font-size: 16px; }
.h-t { font-size: 14px; font-weight: 700; color: var(--ink); }
.h-w { font-size: 11px; color: var(--swim); font-weight: 600; }
.h-wd { font-size: 10px; color: var(--ink-soft); font-family: var(--font-mono); }

/* Sun line */
.sun-line {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 0;
  border-bottom: 1px dashed rgba(230,220,200,0.7);
}
.sun-line:last-child { border-bottom: none; }
.sun-line .ev { color: var(--ink-soft); font-size: 13px; }
.sun-line .t { font-family: var(--font-mono); font-size: 15px; font-weight: 700; color: var(--accent); letter-spacing: 0.02em; }

/* Crowd */
.crowd { display: flex; align-items: center; gap: 10px; }
.crowd-parasols { display: inline-flex; gap: 2px; }
.crowd-meta { display: flex; align-items: baseline; gap: 0; font-size: 12px; }
.crowd-label { font-weight: 700; color: var(--ink); text-transform: lowercase; }
.crowd-peak { color: var(--mute); font-size: 11px; margin-left: 4px; }
.crowd-peak em { font-style: normal; color: var(--ink-soft); font-weight: 600; }

/* AQI */
.aqi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.aqi-cell {
  padding: 10px; background: var(--paper-warm);
  border-radius: 12px; border: 1px solid var(--line);
  display: flex; flex-direction: column; gap: 2px;
}
.aqi-cell .l { font-family: var(--font-mono); font-size: 9px; letter-spacing: 0.06em; color: var(--mute); text-transform: uppercase; }
.aqi-cell .v { font-size: 18px; font-weight: 700; color: var(--ink); font-variant-numeric: tabular-nums; }

.ad-slot { display: flex; flex-direction: column; gap: 4px;
  border: 1px dashed rgba(148,168,180,0.5); border-radius: 14px;
  padding: 8px 12px; background: var(--paper-warm); text-align: center;
  margin: 0 var(--pad) 14px; }
.ad-slot-tag { font-family: var(--font-mono); font-size: 9px; letter-spacing: 0.08em;
  color: var(--mute); text-transform: uppercase; text-align: left; }
.ad-slot iframe { max-width: 600px; margin: 0 auto; background: transparent; }

.footer { text-align: center; padding: 22px var(--pad) 28px; color: var(--mute); font-size: 11px; font-family: var(--font-mono); letter-spacing: 0.02em; }

/* Ships */
.ships-summary {
  font-size: 12px; color: var(--ink-soft);
  margin-bottom: 10px; font-family: var(--font-mono);
  letter-spacing: 0.02em;
}
.ships-summary small { color: var(--mute); }
.ships-empty {
  color: var(--mute); font-style: italic;
  padding: 10px 0; font-size: 13px;
}
.ships-list { display: flex; flex-direction: column; gap: 8px; }
.ship {
  display: flex; gap: 12px; padding: 10px 12px;
  background: var(--paper-warm);
  border: 1px solid var(--line); border-radius: 12px;
}
.ship-ico { font-size: 22px; line-height: 1; padding-top: 2px; }
.ship-body { flex: 1; min-width: 0; }
.ship-h { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.ship-name {
  font-size: 13px; font-weight: 700; color: var(--ink);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  letter-spacing: -0.005em;
}
.ship-flag { font-size: 14px; flex-shrink: 0; }
.ship-meta {
  font-size: 11px; color: var(--accent); margin-top: 3px;
  display: flex; gap: 4px; flex-wrap: wrap;
  font-family: var(--font-mono); font-weight: 600;
}
.ship-meta span:nth-child(even) { color: var(--mute); font-weight: 500; }
.ship-status {
  font-size: 11px; color: var(--ink-soft); margin-top: 2px;
  text-transform: lowercase;
}
.ship-dest { font-size: 11px; color: var(--swim); margin-top: 2px; font-weight: 600; }

/* Satellite */
.sat-pills {
  display: flex; gap: 6px; margin-bottom: 10px;
  overflow-x: auto; scrollbar-width: none;
}
.sat-pills::-webkit-scrollbar { display: none; }
.sat-pill {
  background: var(--paper-warm); color: var(--ink-soft);
  border: 1px solid var(--line); border-radius: 999px;
  padding: 5px 12px; font: inherit; font-size: 11px;
  font-family: var(--font-mono); font-weight: 600;
  letter-spacing: 0.04em; cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  white-space: nowrap;
}
.sat-pill.active {
  background: var(--accent); color: var(--card);
  border-color: var(--accent);
}
.sat-image {
  background: var(--paper-warm); border-radius: 12px;
  overflow: hidden; aspect-ratio: 1/1;
  border: 1px solid var(--line);
}
.sat-image img { width: 100%; height: 100%; object-fit: cover; display: block; }
.sat-cap {
  font-size: 11px; color: var(--ink-soft);
  margin-top: 8px; text-align: center;
  font-family: var(--font-mono); letter-spacing: 0.02em;
}
.sat-empty {
  text-align: center; padding: 28px 14px; color: var(--mute);
  background: var(--paper-warm); border: 1px solid var(--line);
  border-radius: 12px;
}
.sat-empty-ico { font-size: 36px; margin-bottom: 8px; opacity: 0.7; }
.sat-empty-sub {
  font-size: 11px; margin-top: 4px; opacity: 0.85;
  font-family: var(--font-mono); letter-spacing: 0.04em;
}
"""

SHIP_ICONS = {
    "cargueiro": "🚢", "petroleiro": "⛽", "cruzeiro": "🛳",
    "passageiros": "⛴", "pesqueiro": "🎣", "rebocador": "🚤",
    "iate": "⛵", "militar": "⚓", "rápido": "💨",
    "draga": "🏗", "outro": "🛥", "—": "🛥",
}


def country_from_mmsi(mmsi):
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


def render_ships(p, ships_data):
    if not ships_data:
        return ""
    bid = p["id"]
    ships = ships_data.get("by_beach", {}).get(bid, [])
    age_min = (datetime.now().timestamp() - ships_data.get("fetched_at", 0)) / 60

    if not ships:
        return (
            '<section>'
            '<div class="section-tag">navios na costa <span class="sub">50 km</span></div>'
            '<div class="ships-empty">horizonte tranquilo · nenhum navio detectado</div>'
            '</section>'
        )

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
        f'<section>'
        f'<div class="section-tag">navios na costa <span class="sub">50 km · há {age_min:.0f} min</span></div>'
        f'<div class="ships-summary">{len(ships)} navios · {summary}</div>'
        f'<div class="ships-list">{"".join(items)}</div>'
        f'</section>'
    )


def render_satellite(p, sat_data):
    if not sat_data:
        return ""
    records = sat_data.get("by_beach", {}).get(p["id"], [])
    valid = [r for r in records if r.get("status") == "ok"]
    if not valid:
        return '''
  <section>
    <div class="section-tag">satélite <span class="sub">sentinel-2</span></div>
    <div class="sat-empty">
      <div class="sat-empty-ico">☁</div>
      <div>ainda nublado · volte amanhã</div>
      <div class="sat-empty-sub">passa do satélite a cada 5 dias</div>
    </div>
  </section>'''

    label_map = {"hoje": "hoje", "3d": "−3d", "7d": "−7d", "14d": "−14d", "30d": "−30d"}

    pills = "".join(
        f'<button class="sat-pill" data-img="../{r["image"]}" '
        f'data-date="{r["date"]}" data-cloud="{r["cloud"]}">'
        f'{label_map.get(r["label"], r["label"])}</button>'
        for r in valid
    )
    first = valid[0]
    return f'''
  <section>
    <div class="section-tag">satélite <span class="sub">sentinel-2</span></div>
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


def render_score_row_arc(posto, agito_b):
    dials = pick_top_dials(posto, agito_b, n=4)
    cells = []
    for cid, s10, color, label, _sub in dials:
        glyph = render_category_glyph(cid, color="white", size=12)
        cells.append(render_sun_arc(s10 / 10.0, cid, color, size=76, label=label, glyph_html=glyph))
    return f'<div class="score-row">{"".join(cells)}</div>'


def cloud_icon(pct, uv):
    if pct is None: return "·"
    if pct < 25: return "☀" if uv and uv > 0 else "🌙"
    if pct < 60: return "⛅"
    if pct < 90: return "☁"
    return "🌧"


def hourly_cells(hourly, now_hour, max_h=12):
    out = []
    times = hourly.get("time") or []
    n = min(max_h, len(times))
    for i in range(n):
        h_str = times[i][11:13]
        try:
            hod = int(h_str)
        except Exception:
            hod = i
        temp = fmt(hourly["temp_c"][i], "°", 0)
        wave = fmt(hourly["wave_m"][i], "m", 1)
        wind = fmt(hourly["wind_kmh"][i], "", 0)
        wdir = wind_arrow(hourly["wind_dir"][i])
        ico = cloud_icon(hourly["cloud_pct"][i], hourly["uv"][i])
        cls = "h-cell is-now" if hod == now_hour else "h-cell"
        out.append(
            f'<div class="{cls}"><span class="h-hr">{h_str}h</span>'
            f'<span class="h-ico">{ico}</span>'
            f'<span class="h-t">{temp}</span>'
            f'<span class="h-w">{wave}</span>'
            f'<span class="h-wd">{wind} {wdir}</span></div>'
        )
    return '<div class="hourly">' + "".join(out) + "</div>"


def render(p, agito_data=None, now_hour=12, ships_data=None, sat_data=None):
    # Compute scores
    p["_surf"] = surf_score(p)
    p["_swim"] = swim_score(p)
    p["_sun"]  = sun_score(p)
    p["_shade"] = shade_score(p)
    p["_hourly"] = hourly_scores(p)

    yt = p.get("youtube_id")
    if yt:
        cam = (
            f'<iframe src="https://www.youtube.com/embed/{yt}'
            f'?autoplay=1&mute=1&controls=1&modestbranding=1&playsinline=1" '
            'allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>'
        )
    else:
        cam = '<div class="cam-off">câmera ao vivo indisponível</div>'

    w, s, a, ai, sun = p["weather"], p["surf"], p["water"], p["air"], p["sun"]
    h = p.get("hourly", {})
    nh, nl = a.get("next_high_tide"), a.get("next_low_tide")

    state = p.get("state", "")
    eyebrow = f'{p["posto"]}{" · " + state if state else ""}'

    scores = {
        "surfar": p["_surf"], "nadar": p["_swim"],
        "sol": p["_sun"], "evitar_sol": p["_shade"],
    }
    agito_b = (agito_data or {}).get("by_beach", {}).get(p["id"]) if agito_data else None
    score_html = render_score_row_arc(p, agito_b)
    agua_html = render_agua_box(p, _BALNE_BY_BEACH.get(p["id"]), is_detail=True)
    hourly_html = render_hourly_strip(p["_hourly"], now_hour)

    # Best window from top score
    top_act = max(scores, key=scores.get)
    bw = best_window(p["_hourly"].get(top_act, []), 3)
    headlines = {
        "surfar": f"mar bom pra surfar · onda {fmt(s.get('wave_height_m'), 'm')}",
        "nadar":  f"mar manso, água {fmt(a.get('sea_temp_c'), '°', 0)}",
        "sol":    f"bom pro sol · uv {fmt(w.get('uv'), '', 0)}",
        "evitar_sol": "sol ameno, dá pra ficar fora",
    }
    bw_html = (render_best_window(top_act, bw[0], bw[1], headlines[top_act])
               if bw else "")

    # Conditions row
    wd = w.get("wind_dir")
    cond_html = f"""
<div class="cond">
  <div class="cond-i">
    <span class="cond-ico">{_icon('wave')}</span>
    <span class="cond-v">{fmt(s.get('wave_height_m'), '', 1)}<small>m</small></span>
    <span class="cond-l">{fmt(s.get('wave_period_s'), 's', 0)} período</span>
  </div>
  <div class="cond-i">
    <span class="cond-ico">{_icon('drop')}</span>
    <span class="cond-v">{fmt(a.get('sea_temp_c'), '', 0)}<small>°</small></span>
    <span class="cond-l">água</span>
  </div>
  <div class="cond-i">
    <span class="cond-ico">{_icon('wind')}</span>
    <span class="cond-v">{fmt(w.get('wind_kmh'), '', 0)}<small>km/h</small></span>
    <span class="cond-l">{wind_arrow(wd)} {fmt(wd, '°', 0) if wd is not None else '—'}</span>
  </div>
  <div class="cond-i">
    <span class="cond-ico">{_icon('uv')}</span>
    <span class="cond-v">{fmt(w.get('uv'), '', 0)}</span>
    <span class="cond-l">UV {uv_label(w.get('uv'))}</span>
  </div>
</div>"""

    # Extra stats
    extra_html = f"""
<div class="detail-extra">
  <div class="extra"><span class="extra-l">ar</span><span class="extra-v">{fmt(w.get('air_temp_c'), '°', 0)}</span></div>
  <div class="extra"><span class="extra-l">nuvens</span><span class="extra-v">{fmt(w.get('cloud_pct'), '%', 0)}</span></div>
  <div class="extra"><span class="extra-l">aqi</span><span class="extra-v">{fmt(ai.get('aqi'), '', 0)}</span></div>
  <div class="extra"><span class="extra-l">pm2.5</span><span class="extra-v">{fmt(ai.get('pm25'), '', 0)}</span></div>
</div>"""

    # Tide
    tide_chart = tide_svg(h, sun["sunrise"], sun["sunset"]) if h.get("time") else '<div class="empty">sem dados de maré</div>'
    tide_meta_parts = []
    if nh:
        tide_meta_parts.append(
            f'<div class="tide-meta-i"><span class="arr up">↑</span>'
            f'<span class="t">{time_short(nh["time"])}</span>'
            f'<span>{nh["height_m"]:+.2f}m</span></div>'
        )
    if nl:
        tide_meta_parts.append(
            f'<div class="tide-meta-i"><span class="arr dn">↓</span>'
            f'<span class="t">{time_short(nl["time"])}</span>'
            f'<span>{nl["height_m"]:+.2f}m</span></div>'
        )
    tide_meta = f'<div class="tide-meta">{"".join(tide_meta_parts)}</div>' if tide_meta_parts else ""

    # Crowd
    info = (agito_data or {}).get("by_beach", {}).get(p["id"]) if agito_data else None
    bucket = info["current"]["bucket"] if info and info.get("current") else None
    peak = None
    if info:
        np = info.get("next_peak") or info.get("peak")
        if np:
            peak = {"t": time_short(np.get("time")) if np.get("time") else np.get("t", ""),
                    "bucket": np.get("bucket", "")}
    crowd_html = render_crowd_meter(bucket, peak)

    aqi_text, _ = aqi_label(ai.get("aqi"))

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#F4EFE4">
<title>{p['beach']} {p['posto']} — praia smart</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="topbar">
  <a class="back-btn" href="../index.html" aria-label="voltar">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M15 6 L 9 12 L 15 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
  </a>
  <div class="topbar-title">
    <h1>{p['beach']}</h1>
    <div class="topbar-meta">{eyebrow}</div>
  </div>
</header>

<div class="cam">
  {cam}
  <div class="cam-tag"><span class="cam-dot"></span> ao vivo</div>
</div>

<main>

  <section>
    <div class="section-tag">scores <span class="sub">agora</span></div>
    {score_html}
    {bw_html}
  </section>

  {agua_html}

  <section>
    <div class="section-tag">quando ir <span class="sub">próximas 24h</span></div>
    {hourly_html}
  </section>

  {AD_HTML}

  <section>
    <div class="section-tag">condições <span class="sub">agora · {aqi_text}</span></div>
    {cond_html}
    {extra_html}
  </section>

  <section>
    <div class="section-tag">maré <span class="sub">sea-level msl</span></div>
    {tide_meta}
    {tide_chart}
  </section>

  <section>
    <div class="section-tag">próximas horas</div>
    {hourly_cells(h, now_hour) if h.get("time") else ""}
  </section>

  <section>
    <div class="section-tag">sol</div>
    <div class="sun-line"><span class="ev">☀ nasce</span><span class="t">{time_short(sun['sunrise'])}</span></div>
    <div class="sun-line"><span class="ev">☾ põe</span><span class="t">{time_short(sun['sunset'])}</span></div>
  </section>

  <section>
    <div class="section-tag">agito <span class="sub">estimativa</span></div>
    {crowd_html}
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
    agito_data = load_optional(AGITO)
    ships_data = load_optional(SHIPS)
    sat_data = load_optional(SATELLITE)
    now_hour = datetime.now().hour
    for p in postos:
        path = os.path.join(OUTDIR, f"{p['id']}.html")
        open(path, "w").write(render(p, agito_data, now_hour, ships_data, sat_data))
    print(f"Wrote {len(postos)} detail pages to {OUTDIR}")


if __name__ == "__main__":
    main()
