"""Generate web/index.html from data/conditions.json.

Mobile-first. Leads with cross-posto winners ("qual praia pra X agora"),
sorts cards by surf score, badges/highlights notable values.

Visual redesign: light "praia 10am" beach palette, sun-arc score viz,
24h activity strip, parasol crowd meter, Plus Jakarta Sans + Instrument
Serif italic wordmark.
"""
import json
import math
import os
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "conditions.json")
ALERTS = os.path.join(ROOT, "data", "alerts.json")
NEWS = os.path.join(ROOT, "data", "news.json")
AGITO = os.path.join(ROOT, "data", "agito.json")
BALNEABILIDADE = os.path.join(ROOT, "data", "balneabilidade.json")
OUT = os.path.join(ROOT, "web", "index.html")

BUCKET_CLASS = {"vazia": "v", "moderada": "m", "cheia": "c", "lotada": "l"}
BUCKET_INDEX = {"vazia": 1, "moderada": 2, "cheia": 3, "lotada": 4}

AD_HTML = """
<div class="ad-slot">
  <div class="ad-slot-tag">anúncio</div>
  <iframe data-aa='2438146' src='//acceptable.a-ads.com/2438146/?size=Adaptive'
    style='border:0;padding:0;width:70%;height:90px;overflow:hidden;display:block;margin:auto;background:transparent;'></iframe>
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


def _bell(x, center, width):
    try:
        return math.exp(-((x - center) ** 2) / (2 * width ** 2))
    except Exception:
        return 0


# ─────────────────────────────────────────────────────────────
# Current-condition scores (used to sort cards + pick hero)
# ─────────────────────────────────────────────────────────────

def surf_score(p):
    s, w = p["surf"], p["weather"]
    h = s.get("wave_height_m") or 0
    period = s.get("wave_period_s") or 0
    wind = w.get("wind_kmh") or 0
    if h < 0.4 or h > 3.0:
        size = 0
    else:
        size = max(0.0, 1 - abs(h - 1.5) / 1.5)
    period_score = min(period / 14, 1.0)
    offshore = max(0, offshore_component(w.get("wind_dir"))) * min(wind / 15, 1.0)
    return round(size * 0.5 + period_score * 0.3 + offshore * 0.2, 3)


def swim_score(p):
    s, a = p["surf"], p["water"]
    h = s.get("wave_height_m") or 0
    temp = a.get("sea_temp_c") or 0
    calm = 1 / (1 + h)
    warmth = max(0, min((temp - 18) / 12, 1.0))
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


def shade_score(p):
    """'Evitar sol' — bright outside but UV mild."""
    w = p["weather"]
    uv = w.get("uv") or 0
    cloud = w.get("cloud_pct") or 0
    if uv <= 0:
        return 0
    mild = max(0, 1 - uv / 6)
    light = (100 - cloud) / 100
    return round(mild * 0.6 + light * 0.4, 3)


# ─────────────────────────────────────────────────────────────
# Hourly scoring (per-activity 24-bar strip)
# ─────────────────────────────────────────────────────────────

def hourly_scores(p):
    """Return {surfar:[24], nadar:[24], sol:[24], evitar_sol:[24]}.

    Reads hourly arrays from p['hourly'] when present, otherwise falls back
    to flat arrays scaled by the current condition score.
    """
    out = {"surfar": [0.0] * 24, "nadar": [0.0] * 24, "sol": [0.0] * 24, "evitar_sol": [0.0] * 24}
    hh = p.get("hourly") or {}
    times = hh.get("time") or []
    n = min(24, len(times))
    if n == 0:
        # fallback to flat current-score bars
        return {
            "surfar":     [p["_surf"]] * 24,
            "nadar":      [p["_swim"]] * 24,
            "sol":        [p["_sun"]] * 24,
            "evitar_sol": [shade_score(p)] * 24,
        }

    sea_t = (p.get("water") or {}).get("sea_temp_c") or 0
    waves = hh.get("wave_m") or []
    periods = hh.get("wave_period_s") or []
    winds = hh.get("wind_kmh") or []
    wdirs = hh.get("wind_dir") or []
    uvs = hh.get("uv") or []
    clouds = hh.get("cloud_pct") or []

    def g(arr, i, default=0):
        return arr[i] if i < len(arr) and arr[i] is not None else default

    for i in range(n):
        # parse hour-of-day from ISO time
        try:
            hod = int(times[i][11:13])
        except Exception:
            hod = i % 24
        wv = g(waves, i); per = g(periods, i); wd = g(winds, i)
        wdr = wdirs[i] if i < len(wdirs) else None
        uv = g(uvs, i); cl = g(clouds, i)

        # surfar
        size = _bell(wv, 1.5, 0.9) if 0.4 <= wv <= 3.0 else 0
        per_s = min(per / 14, 1.0)
        offsh = max(0, offshore_component(wdr)) * min(wd / 12, 1.0)
        daylight = 1.0 if uv > 0 else 0.2
        surfar = daylight * (size * 0.5 + per_s * 0.3 + offsh * 0.2)

        # nadar
        calm = 1 / (1 + wv)
        warmth = max(0, min((sea_t - 18) / 12, 1.0))
        # only meaningful in daylight
        nadar = (calm * 0.6 + warmth * 0.4) * (1.0 if uv > 0 else 0.25)

        # sol (tan-zone)
        if uv <= 0:
            sol = 0
        elif uv < 3:
            uv_s = uv / 3 * 0.6
            clear = (100 - cl) / 100
            breeze = max(0, 1 - wd / 25)
            sol = uv_s * 0.5 + clear * 0.3 + breeze * 0.2
        elif uv <= 7:
            clear = (100 - cl) / 100
            breeze = max(0, 1 - wd / 25)
            sol = 1.0 * 0.5 + clear * 0.3 + breeze * 0.2
        else:
            uv_s = max(0, 1 - (uv - 7) / 4)
            clear = (100 - cl) / 100
            breeze = max(0, 1 - wd / 25)
            sol = uv_s * 0.5 + clear * 0.3 + breeze * 0.2

        # evitar_sol — bright but mild UV
        if uv <= 0:
            evitar = 0
        else:
            mild = max(0, 1 - uv / 6)
            light = (100 - cl) / 100
            evitar = mild * 0.6 + light * 0.4

        # store by hour-of-day so bars line up to 00–23
        out["surfar"][hod]     = max(out["surfar"][hod], round(surfar, 3))
        out["nadar"][hod]      = max(out["nadar"][hod], round(nadar, 3))
        out["sol"][hod]        = max(out["sol"][hod], round(sol, 3))
        out["evitar_sol"][hod] = max(out["evitar_sol"][hod], round(evitar, 3))

    return out


def best_window(hours, length=3):
    if not hours or max(hours) <= 0.05:
        return None
    best_sum, best_i = -1, 0
    for i in range(0, max(1, 24 - length + 1)):
        s = sum(hours[i:i + length])
        if s > best_sum:
            best_sum, best_i = s, i
    return (best_i, best_i + length)


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


# ─────────────────────────────────────────────────────────────
# Visual primitives — return inline HTML/SVG strings
# ─────────────────────────────────────────────────────────────

ACTIVITY_LABEL = {
    "surfar": "surfar", "nadar": "nadar", "sol": "sol forte", "evitar_sol": "sol tranquilo",
}
ACTIVITY_VAR = {
    "surfar": "var(--surf)", "nadar": "var(--swim)",
    "sol": "var(--sun)", "evitar_sol": "var(--shade)",
}


def render_activity_glyph(activity, color="currentColor", size=14):
    s = size
    if activity == "surfar":
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M2 15 C 5 11, 8 11, 11 14 S 17 17, 22 13" stroke="{color}" stroke-width="2.2" stroke-linecap="round" fill="none"/>'
                f'<path d="M2 19 C 5 16, 8 16, 11 18 S 17 20, 22 17" stroke="{color}" stroke-width="2.2" stroke-linecap="round" fill="none" opacity="0.5"/>'
                f'</svg>')
    if activity == "nadar":
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M12 3 C 12 3, 5 11, 5 16 a 7 7 0 0 0 14 0 C 19 11, 12 3, 12 3 Z" stroke="{color}" stroke-width="2" fill="none" stroke-linejoin="round"/>'
                f'</svg>')
    if activity == "sol":
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<circle cx="12" cy="12" r="4" stroke="{color}" stroke-width="2" fill="none"/>'
                f'<g stroke="{color}" stroke-width="2" stroke-linecap="round">'
                f'<line x1="12" y1="2" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="22"/>'
                f'<line x1="2" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="22" y2="12"/>'
                f'<line x1="4.9" y1="4.9" x2="6.3" y2="6.3"/><line x1="17.7" y1="17.7" x2="19.1" y2="19.1"/>'
                f'<line x1="4.9" y1="19.1" x2="6.3" y2="17.7"/><line x1="17.7" y1="6.3" x2="19.1" y2="4.9"/>'
                f'</g></svg>')
    if activity == "evitar_sol":
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M5 16 a 7 7 0 0 1 14 0" stroke="{color}" stroke-width="2" fill="none" stroke-linecap="round"/>'
                f'<line x1="3" y1="20" x2="21" y2="20" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
                f'<g stroke="{color}" stroke-width="2" stroke-linecap="round">'
                f'<line x1="12" y1="3" x2="12" y2="5"/>'
                f'<line x1="4.5" y1="9" x2="5.9" y2="10.4"/>'
                f'<line x1="19.5" y1="9" x2="18.1" y2="10.4"/>'
                f'</g></svg>')
    return ""


def render_sun_arc(score, activity, color_var, size=80, label=None, glyph_html=None):
    """Inline SVG semicircle arc, filled proportionally to score [0,1].

    `activity` is used to look up the default glyph + label when no override
    is passed. Pass `label` and/or `glyph_html` to use a custom category.
    """
    score = max(0.0, min(1.0, score or 0))
    cx, cy, r = 50, 52, 38
    PR = math.pi * r
    filled = max(0.001, score)
    theta = math.pi * (1 - filled)
    hx = cx + r * math.cos(theta)
    hy = cy - r * math.sin(theta)
    score10 = round(score * 10)
    h = round(size * 0.78)
    arc_path = f'M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}'

    ticks = []
    for t in (0.25, 0.5, 0.75):
        a = math.pi * (1 - t)
        x1 = cx + (r - 9) * math.cos(a); y1 = cy - (r - 9) * math.sin(a)
        x2 = cx + (r - 3) * math.cos(a); y2 = cy - (r - 3) * math.sin(a)
        ticks.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="var(--track-tick)" stroke-width="1.3" stroke-linecap="round"/>')

    if glyph_html is None:
        glyph_html = render_activity_glyph(activity, color="white", size=12)
    if label is None:
        label = ACTIVITY_LABEL.get(activity, activity)

    return (
        f'<div class="sa">'
        f'<svg width="{size}" height="{h}" viewBox="0 0 100 78" style="display:block">'
        f'<path d="{arc_path}" stroke="var(--track)" stroke-width="7" stroke-linecap="round" fill="none"/>'
        f'{"".join(ticks)}'
        f'<path d="{arc_path}" stroke="{color_var}" stroke-width="7" stroke-linecap="round" fill="none"'
        f' stroke-dasharray="{filled * PR:.2f} {PR:.2f}"/>'
        f'<circle cx="{hx:.2f}" cy="{hy:.2f}" r="9" fill="{color_var}"/>'
        f'<g transform="translate({hx - 6:.2f} {hy - 6:.2f})">{glyph_html}</g>'
        f'<text x="{cx}" y="{cy + 4}" text-anchor="middle"'
        f' font-family="\'Plus Jakarta Sans\', sans-serif" font-size="20" fill="var(--ink)"'
        f' font-weight="700" letter-spacing="-0.02em">{score10}</text>'
        f'</svg>'
        f'<div class="sa-label">{label}</div>'
        f'</div>'
    )


# ─────────────────────────────────────────────────────────────
# Dynamic top-4-of-10 category dial system
# ─────────────────────────────────────────────────────────────

def render_category_glyph(cat_id, color="currentColor", size=12):
    s = size
    if cat_id == "publico":
        # 3 heads + shoulders
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<circle cx="6" cy="9" r="2.2" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
                f'<circle cx="12" cy="7.5" r="2.5" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
                f'<circle cx="18" cy="9" r="2.2" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
                f'<path d="M2.5 19 q 3.5 -5 9.5 -5 t 9.5 5" stroke="{color}" stroke-width="2" stroke-linecap="round" fill="none"/>'
                f'</svg>')
    if cat_id == "ar":
        # leaf
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M5 19 C 5 11, 11 5, 19 5 C 19 13, 13 19, 5 19 Z" stroke="{color}" stroke-width="2" stroke-linejoin="round" fill="none"/>'
                f'<path d="M5 19 L 14 10" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
                f'</svg>')
    if cat_id == "uv":
        return render_activity_glyph("sol", color=color, size=size)
    if cat_id == "ondas":
        return render_activity_glyph("surfar", color=color, size=size)
    if cat_id == "vento":
        # wind streaks
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M3 8 H 14 a 3 3 0 1 0 -3 -3" stroke="{color}" stroke-width="2" stroke-linecap="round" fill="none"/>'
                f'<path d="M3 13 H 19" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
                f'<path d="M3 18 H 16 a 3 3 0 1 1 -3 3" stroke="{color}" stroke-width="2" stroke-linecap="round" fill="none"/>'
                f'</svg>')
    if cat_id == "calor":
        # thermometer
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M12 3 a 2.5 2.5 0 0 1 2.5 2.5 V 14 a 4 4 0 1 1 -5 0 V 5.5 A 2.5 2.5 0 0 1 12 3 Z" stroke="{color}" stroke-width="2" stroke-linejoin="round" fill="none"/>'
                f'<circle cx="12" cy="18" r="1.6" fill="{color}"/>'
                f'</svg>')
    if cat_id == "mar_quente":
        return render_activity_glyph("nadar", color=color, size=size)
    if cat_id == "ceu":
        # cloud
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M7 18 a 4 4 0 0 1 -0.6 -7.95 a 5.5 5.5 0 0 1 10.6 1.45 a 3.5 3.5 0 0 1 0 7 Z" stroke="{color}" stroke-width="2" stroke-linejoin="round" fill="none"/>'
                f'</svg>')
    if cat_id == "mare":
        # wave curve + small up arrow
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M2 16 C 6 12, 10 12, 12 14 S 18 18, 22 14" stroke="{color}" stroke-width="2" stroke-linecap="round" fill="none"/>'
                f'<path d="M17 8 L 20 5 L 23 8 M 20 5 V 12" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
                f'</svg>')
    if cat_id == "agua_limpa":
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M12 3 C 12 3, 5 11, 5 16 a 7 7 0 0 0 14 0 C 19 11, 12 3, 12 3 Z" stroke="{color}" stroke-width="2" fill="none"/>'
                f'<path d="M9 15 L 11 17 L 15 13" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
                f'</svg>')
    return ""


# ── Scorers: each returns (score_0_to_10 | None, sublabel | None) ──

def _clamp10(v):
    if v is None: return None
    return max(0, min(10, round(v)))


def score_publico(posto, agito_b):
    if not agito_b or not agito_b.get("current"):
        return (None, None)
    s = agito_b["current"].get("score")
    if s is None:
        return (None, None)
    # invert: emptier = better score on dial? The label is "público" — we show
    # how crowded it is, with higher = more crowded. Keep raw score for now.
    return (_clamp10(s * 10), agito_b["current"].get("bucket"))


def score_ar(posto):
    aqi = (posto.get("air") or {}).get("aqi")
    if aqi is None:
        return (None, None)
    # piecewise: 0→10, 50→8, 100→5, 150→3, 200+→1
    if aqi <= 0: v = 10
    elif aqi <= 50:  v = 10 - (aqi / 50) * 2
    elif aqi <= 100: v = 8 - ((aqi - 50) / 50) * 3
    elif aqi <= 150: v = 5 - ((aqi - 100) / 50) * 2
    elif aqi <= 200: v = 3 - ((aqi - 150) / 50) * 2
    else: v = 1
    return (_clamp10(v), None)


def score_uv(posto):
    uv = (posto.get("weather") or {}).get("uv")
    if uv is None:
        return (None, None)
    if uv <= 2: v = 10
    elif uv <= 5: v = 8
    elif uv <= 7: v = 5
    elif uv <= 10: v = 3
    else: v = 1
    return (_clamp10(v), uv_label(uv))


def score_ondas(posto):
    h = (posto.get("surf") or {}).get("wave_height_m")
    if h is None:
        return (None, None)
    # bell ~1.5m → 10, 0 → 1, >3 → ~3
    if h <= 0:
        v = 1
    elif h > 3:
        v = max(2, 4 - (h - 3))
    else:
        v = 1 + 9 * math.exp(-((h - 1.5) ** 2) / (2 * 0.9 ** 2))
    return (_clamp10(v), f"{h:.1f}m")


def score_vento(posto):
    w = (posto.get("weather") or {}).get("wind_kmh")
    if w is None:
        return (None, None)
    if w < 1:
        v = 4
    elif w <= 5:
        v = 4 + (w - 1) * (6 / 4)  # 4 → 10 at 5
    elif w <= 15:
        v = 10
    elif w <= 30:
        v = 10 - (w - 15) * (8 / 15)  # → 2 at 30
    else:
        v = max(1, 2 - (w - 30) * 0.05)
    return (_clamp10(v), f"{w:.0f} km/h")


def score_calor(posto):
    t = (posto.get("weather") or {}).get("air_temp_c")
    if t is None:
        return (None, None)
    # bell: 28→10, 20→5, 35→5, <15→1, >40→1
    if t < 15 or t > 40:
        v = 1
    else:
        v = 1 + 9 * math.exp(-((t - 28) ** 2) / (2 * 5.0 ** 2))
    return (_clamp10(v), f"{t:.0f}°")


def score_mar_quente(posto):
    t = (posto.get("water") or {}).get("sea_temp_c")
    if t is None:
        return (None, None)
    if t >= 26: v = 10
    elif t >= 24: v = 8
    elif t >= 22: v = 6
    elif t >= 20: v = 4
    else: v = 2
    return (_clamp10(v), f"{t:.0f}°")


def score_ceu(posto):
    cl = (posto.get("weather") or {}).get("cloud_pct")
    if cl is None:
        return (None, None)
    v = 10 - (cl / 100) * 9  # 0→10, 100→1
    return (_clamp10(v), f"{cl:.0f}% nuvem")


def score_mare(posto):
    water = posto.get("water") or {}
    nh = water.get("next_high_tide") or {}
    nl = water.get("next_low_tide") or {}
    nh_t, nl_t = nh.get("time"), nl.get("time")
    nh_h, nl_h = nh.get("height_m"), nl.get("height_m")
    if not (nh_t and nl_t and nh_h is not None and nl_h is not None):
        return (None, None)
    try:
        now = datetime.now()
        th = datetime.fromisoformat(nh_t)
        tl = datetime.fromisoformat(nl_t)
    except Exception:
        return (None, None)
    # rising if next high is sooner than next low
    rising = th < tl
    if rising:
        # Time since previous low ≈ time from now until tl minus the cycle.
        # Simpler: position on the rise from low→high. Approximate using
        # remaining time to next high vs ~6h half-cycle.
        remaining = (th - now).total_seconds() / 3600
        frac = max(0.0, min(1.0, 1 - remaining / 6.0))  # 0=just past low, 1=at high
        status = "subindo"
    else:
        remaining = (tl - now).total_seconds() / 3600
        frac = max(0.0, min(1.0, remaining / 6.0))  # 1=at high, 0=at low
        status = "descendo"
    # Map fraction to 0-10 "tide height percentile"
    v = 1 + 9 * frac
    return (_clamp10(v), status)


_BALNE = load_optional(BALNEABILIDADE) or {}
_BALNE_BY_BEACH = _BALNE.get("by_beach", {}) if isinstance(_BALNE, dict) else {}


def _balne_sublabel(entry):
    src = entry.get("source") or "—"
    rd = entry.get("report_date")
    if not rd:
        return src
    try:
        d = datetime.strptime(rd, "%Y-%m-%d").date()
        days = (date.today() - d).days
        if days <= 0:
            when = "hoje"
        elif days == 1:
            when = "ontem"
        else:
            when = f"{days} dias atrás"
        return f"{src} · {when}"
    except Exception:
        return f"{src} · {rd}"


def score_agua_limpa(posto):
    entry = _BALNE_BY_BEACH.get(posto.get("id"))
    if not entry:
        return (None, None)
    status = entry.get("status")
    if status == "propria":
        return (10, f"própria — {_balne_sublabel(entry)}")
    if status == "alerta":
        return (5, f"alerta — {_balne_sublabel(entry)}")
    if status == "impropria":
        return (1, f"imprópria — {_balne_sublabel(entry)}")
    return (None, None)


CATEGORIES = {
    "publico":    {"label": "público",    "color_var": "var(--accent)", "scorer": score_publico,    "needs_agito": True},
    "ar":         {"label": "ar",         "color_var": "var(--shade)",  "scorer": score_ar,         "needs_agito": False},
    "uv":         {"label": "uv",         "color_var": "var(--sun)",    "scorer": score_uv,         "needs_agito": False},
    "ondas":      {"label": "ondas",      "color_var": "var(--surf)",   "scorer": score_ondas,      "needs_agito": False},
    "vento":      {"label": "vento",      "color_var": "var(--swim)",   "scorer": score_vento,      "needs_agito": False},
    "calor":      {"label": "calor",      "color_var": "var(--surf)",   "scorer": score_calor,      "needs_agito": False},
    "mar_quente": {"label": "mar quente", "color_var": "var(--swim)",   "scorer": score_mar_quente, "needs_agito": False},
    "ceu":        {"label": "céu",        "color_var": "var(--sun)",    "scorer": score_ceu,        "needs_agito": False},
    "mare":       {"label": "maré",       "color_var": "var(--swim)",   "scorer": score_mare,       "needs_agito": False},
    "agua_limpa": {"label": "água limpa", "color_var": "var(--shade)",  "scorer": score_agua_limpa, "needs_agito": False},
}


def _notability(cat_id, posto):
    """Distance from 'neutral' for this metric. Higher = more notable."""
    w = posto.get("weather") or {}
    s = posto.get("surf") or {}
    a = posto.get("water") or {}
    air = posto.get("air") or {}
    # Notability normalized roughly 0-1 per metric.
    if cat_id == "ondas":
        h = s.get("wave_height_m") or 0
        # bigger waves more notable; flat sea also notable
        return min(1.0, abs(h - 0.8) / 1.5 + h / 4)
    if cat_id == "vento":
        v = w.get("wind_kmh")
        if v is None: return 0
        return min(1.0, abs(v - 10) / 20)
    if cat_id == "calor":
        t = w.get("air_temp_c")
        if t is None: return 0
        return min(1.0, abs(t - 25) / 10)
    if cat_id == "ceu":
        cl = w.get("cloud_pct")
        if cl is None: return 0
        return abs(cl - 50) / 50
    if cat_id == "mar_quente":
        t = a.get("sea_temp_c")
        if t is None: return 0
        return min(1.0, abs(t - 22) / 6)
    if cat_id == "ar":
        aqi = air.get("aqi")
        if aqi is None: return 0
        return min(1.0, abs(aqi - 25) / 50)
    if cat_id == "mare":
        return 0.4
    if cat_id == "agua_limpa":
        entry = _BALNE_BY_BEACH.get(posto.get("id"))
        if not entry:
            return 0
        st = entry.get("status")
        if st == "impropria":
            return 0.9
        if st == "alerta":
            return 0.7
        if st == "propria":
            return 0.5
        return 0
    return 0


def pick_top_dials(posto, agito_b, n=4):
    """Return [(cat_id, score10, color_var, label, sublabel)] of length up to n."""
    scored = {}
    for cid, meta in CATEGORIES.items():
        s10, sub = meta["scorer"](posto, agito_b) if meta["needs_agito"] else meta["scorer"](posto)
        if s10 is None:
            continue
        scored[cid] = (s10, sub)

    chosen = []
    # Always include publico + uv if data exists
    for must in ("publico", "uv"):
        if must in scored and must not in chosen:
            chosen.append(must)

    # Rank remainder by notability
    rest = [cid for cid in scored if cid not in chosen]
    rest.sort(key=lambda c: -_notability(c, posto))
    for cid in rest:
        if len(chosen) >= n: break
        chosen.append(cid)

    out = []
    for cid in chosen[:n]:
        s10, sub = scored[cid]
        meta = CATEGORIES[cid]
        out.append((cid, s10, meta["color_var"], meta["label"], sub))
    return out


def render_dynamic_score_row(posto, agito_b):
    dials = pick_top_dials(posto, agito_b, n=4)
    cells = []
    for cid, s10, color, label, _sub in dials:
        glyph = render_category_glyph(cid, color="white", size=12)
        cells.append(render_sun_arc(s10 / 10.0, cid, color, size=76, label=label, glyph_html=glyph))
    return f'<div class="score-row score-row--arc">{"".join(cells)}</div>'


def render_score_row(scores):
    """Sun-arc dial for each of 4 activities."""
    items = [
        ("surfar", "var(--surf)"),
        ("nadar", "var(--swim)"),
        ("sol", "var(--sun)"),
        ("evitar_sol", "var(--shade)"),
    ]
    cells = "".join(render_sun_arc(scores.get(a, 0), a, c, size=76) for a, c in items)
    return f'<div class="score-row score-row--arc">{cells}</div>'


def render_hourly_row(activity, hours, color_var, now_hour):
    if not hours:
        hours = [0] * 24
    inactive = max(hours) < 0.1
    bw = best_window(hours, 3) if not inactive else None
    bars = []
    for h in range(24):
        v = hours[h] if h < len(hours) else 0
        height = max(2, v * 22)
        cls = "hs-bar"
        if h == now_hour: cls += " is-now"
        if bw and bw[0] <= h < bw[1]: cls += " in-win"
        bars.append(
            f'<div class="{cls}" style="--h:{height:.1f}px;--c:{color_var}"'
            f' title="{h:02d}h · {v * 10:.1f}"></div>'
        )
    now_line = (f'<div class="hs-now-line" style="left:calc({(now_hour + 0.5) / 24 * 100:.2f}%)"></div>')
    win_underline = ""
    if bw:
        win_underline = (f'<div class="hs-window-underline"'
                         f' style="left:{bw[0] / 24 * 100:.2f}%;width:{3 / 24 * 100:.2f}%;background:{color_var}"></div>')
    win_label = (f'{bw[0]:02d}–{bw[1]:02d}h' if bw else '—')
    glyph = render_activity_glyph(activity, color=color_var, size=12)
    return (
        f'<div class="hs-row">'
        f'<div class="hs-label">{glyph}<span>{ACTIVITY_LABEL[activity]}</span></div>'
        f'<div class="hs-bars">{"".join(bars)}{now_line}{win_underline}</div>'
        f'<div class="hs-window-label" style="color:{color_var}">{win_label}</div>'
        f'</div>'
    )


def render_hourly_strip(hourly, now_hour):
    rows = [
        ("surfar", "var(--surf)"),
        ("nadar", "var(--swim)"),
        ("sol", "var(--sun)"),
        ("evitar_sol", "var(--shade)"),
    ]
    rows_html = "".join(render_hourly_row(a, hourly.get(a, []), c, now_hour) for a, c in rows)
    return (
        f'<div class="hs">'
        f'<div class="hs-axis"><span>00</span><span>06</span>'
        f'<span style="color:var(--accent);font-weight:700">agora</span>'
        f'<span>12</span><span>18</span><span>24</span></div>'
        f'{rows_html}'
        f'</div>'
    )


def render_best_window(activity, start_hour, end_hour, headline):
    if start_hour is None:
        return ""
    color_var = ACTIVITY_VAR[activity]
    return (
        f'<div class="bw" style="--bw-c:{color_var}">'
        f'<span class="bw-bar"></span>'
        f'<div class="bw-text">{headline}</div>'
        f'<div class="bw-window">{start_hour:02d}–{end_hour:02d}h</div>'
        f'</div>'
    )


def render_parasol(filled, color):
    fill = color if filled else "none"
    return (f'<svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
            f'<path d="M3 11 a 9 6 0 0 1 18 0 Z" stroke="{color}" stroke-width="1.8" fill="{fill}" stroke-linejoin="round"/>'
            f'<line x1="12" y1="11" x2="12" y2="21" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/>'
            f'<path d="M12 21 q 2 0 2 -2" stroke="{color}" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
            f'</svg>')


def render_crowd_meter(bucket, peak=None):
    if not bucket:
        return ('<div class="crowd"><div class="crowd-parasols">'
                + "".join(render_parasol(False, "var(--mute)") for _ in range(4))
                + '</div><div class="crowd-meta"><span class="crowd-label" style="color:var(--mute)">—</span></div></div>')
    idx = BUCKET_INDEX.get(bucket, 2)
    parasols = "".join(
        render_parasol(i < idx, "var(--accent)" if i < idx else "var(--mute)")
        for i in range(4)
    )
    peak_html = ""
    if peak:
        peak_html = f'<span class="crowd-peak">· pico {peak.get("t","")} <em>{peak.get("bucket","")}</em></span>'
    return (f'<div class="crowd">'
            f'<div class="crowd-parasols">{parasols}</div>'
            f'<div class="crowd-meta"><span class="crowd-label">{bucket}</span>{peak_html}</div>'
            f'</div>')


# Tiny inline icons for conditions row
def _icon(name, size=14):
    s = size
    if name == "wave":
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M2 14 C 5 11, 8 11, 11 13 S 17 16, 22 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
                f'<path d="M2 18 C 5 15, 8 15, 11 17 S 17 20, 22 16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" opacity="0.5"/>'
                f'</svg>')
    if name == "drop":
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M12 3 C 12 3, 5 11, 5 16 a 7 7 0 0 0 14 0 C 19 11, 12 3, 12 3 Z" stroke="currentColor" stroke-width="1.8" fill="none"/>'
                f'</svg>')
    if name == "wind":
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M3 9 H 14 a 3 3 0 1 0 -3 -3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" fill="none"/>'
                f'<path d="M3 15 H 18 a 3 3 0 1 1 -3 3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" fill="none"/>'
                f'</svg>')
    if name == "uv":
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<circle cx="12" cy="12" r="3.5" stroke="currentColor" stroke-width="1.8"/>'
                f'<g stroke="currentColor" stroke-width="1.8" stroke-linecap="round">'
                f'<line x1="12" y1="3" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="21"/>'
                f'<line x1="3" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="21" y2="12"/>'
                f'</g></svg>')
    if name == "pin":
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M12 2 a 7 7 0 0 1 7 7 c 0 5 -7 13 -7 13 S 5 14 5 9 a 7 7 0 0 1 7 -7 Z" stroke="currentColor" stroke-width="1.8"/>'
                f'<circle cx="12" cy="9" r="2.4" stroke="currentColor" stroke-width="1.8"/>'
                f'</svg>')
    if name == "chev":
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                f'<path d="M9 6 L 15 12 L 9 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
                f'</svg>')
    return ""


def uv_label(uv):
    if uv is None or uv == 0: return "—"
    if uv < 3: return "mole"
    if uv < 6: return "ok"
    if uv < 8: return "forte"
    return "extremo"


# ─────────────────────────────────────────────────────────────
# Card render
# ─────────────────────────────────────────────────────────────

def render_card(p, marks, agito_data=None, now_hour=12):
    w, s, a = p["weather"], p["surf"], p["water"]

    badges = []
    if marks.get("surf") == p["id"]:
        badges.append('<span class="badge badge--surf">melhor onda</span>')
    if marks.get("swim") == p["id"]:
        badges.append('<span class="badge badge--swim">mais calma</span>')
    if marks.get("warmest") == p["id"]:
        badges.append('<span class="badge badge--warm">água quente</span>')
    badges_html = "".join(badges)

    yt = p.get("youtube_id")
    if yt:
        cam = (
            f'<div class="card-cam" aria-label="câmera ao vivo">'
            f'<img src="https://i.ytimg.com/vi/{yt}/mqdefault.jpg" alt="" loading="lazy"/>'
            f'<div class="card-cam-dot"></div>'
            f'<div class="card-cam-tag">ao vivo</div>'
            f'</div>'
        )
    else:
        cam = '<div class="card-cam card-cam--off"><div class="card-cam-off-text">sem cam</div></div>'

    scores = {
        "surfar": p["_surf"], "nadar": p["_swim"],
        "sol": p["_sun"], "evitar_sol": p["_shade"],
    }
    agito_b = (agito_data or {}).get("by_beach", {}).get(p["id"]) if agito_data else None
    score_row = render_dynamic_score_row(p, agito_b)
    hourly_html = render_hourly_strip(p["_hourly"], now_hour)

    # Best window from the top-scoring activity
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

    # Crowd footer
    info = (agito_data or {}).get("by_beach", {}).get(p["id"]) if agito_data else None
    bucket = info["current"]["bucket"] if info and info.get("current") else None
    peak = None
    if info:
        np = info.get("next_peak") or info.get("peak")
        if np:
            peak = {"t": time_short(np.get("time")) if np.get("time") else np.get("t", ""),
                    "bucket": np.get("bucket", "")}
    crowd_html = render_crowd_meter(bucket, peak)

    return f"""
<article class="card" data-state="{p.get('state','?')}" data-surf="{p['_surf']}" data-swim="{p['_swim']}" data-sun="{p['_sun']}">
  <header class="card-h">
    <div class="card-h-l">
      <h3 class="card-name">{p['beach']}</h3>
      <div class="card-meta">
        <span class="card-posto">{_icon('pin', 11)} {p['posto']}</span>
        <span class="card-state">{p.get('state','')}</span>
        {badges_html}
      </div>
    </div>
    <a href="beach/{p['id']}.html" aria-label="ver câmera">{cam}</a>
  </header>
  {score_row}
  {hourly_html}
  {bw_html}
  {cond_html}
  <footer class="card-f">
    {crowd_html}
    <a class="card-cta" href="beach/{p['id']}.html">ver detalhes {_icon('chev', 12)}</a>
  </footer>
</article>
"""


# ─────────────────────────────────────────────────────────────
# Hero strip
# ─────────────────────────────────────────────────────────────

def render_hero_card(key, title, activity, color_var, beach, why, score):
    return f"""
<a class="hero-card hero-card--{key}" style="--c:{color_var}" href="beach/{beach['id']}.html">
  <div class="hero-card__title">
    {render_activity_glyph(activity, color=color_var, size=14)}
    <span>{title}</span>
    <span class="hero-card__now">agora</span>
  </div>
  <div class="hero-card__name">{beach['beach']}</div>
  <div class="hero-card__reason">{why}</div>
  <div class="hero-card__arc">{render_sun_arc(score, activity, color_var, size=64)}</div>
  <div class="hero-card__shimmer" aria-hidden="true"></div>
</a>"""


# ─────────────────────────────────────────────────────────────
# CSS — light "praia 10am" palette
# ─────────────────────────────────────────────────────────────

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
  margin: 0; padding: 0;
  background:
    radial-gradient(900px 600px at 20% 0%, #f1ecdf 0%, transparent 50%),
    radial-gradient(800px 700px at 100% 30%, #e5eef2 0%, transparent 55%),
    linear-gradient(180deg, #efe9da 0%, #e9e4d2 100%);
  background-attachment: fixed;
  color: var(--ink);
  font-family: var(--font-sans);
  font-size: 15px; line-height: 1.4;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
body { padding-bottom: env(safe-area-inset-bottom); }
a { color: inherit; text-decoration: none; }

/* ── Topbar ───────────────────────────────────────────── */
.topbar {
  position: sticky; top: 0; z-index: 10;
  background: linear-gradient(180deg, var(--paper) 70%, rgba(244,239,228,0.85) 100%);
  backdrop-filter: blur(10px);
  padding: 12px var(--pad) 10px;
  padding-top: calc(12px + env(safe-area-inset-top));
  border-bottom: 1px solid rgba(230,220,200,0.7);
}
.topbar-row1 { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.wordmark { display: inline-flex; align-items: baseline; gap: 6px; letter-spacing: -0.01em; }
.wordmark .wm-praia {
  font-family: var(--font-serif); font-style: italic; font-weight: 400;
  font-size: 42px; line-height: 1; color: var(--accent);
  margin-right: -1px; letter-spacing: -0.02em;
}
.wordmark .wm-smart {
  font-family: var(--font-sans); font-weight: 700;
  font-size: 26px; letter-spacing: -0.005em; color: var(--ink);
}
.topbar-sub {
  display: flex; align-items: center; gap: 7px;
  font-size: 12px; color: var(--ink-soft); margin-top: 8px;
  font-family: var(--font-mono); letter-spacing: 0.02em;
}
.dot { width: 7px; height: 7px; border-radius: 50%; background: var(--good); display: inline-block; }
.dot--live { animation: live-pulse 2.4s infinite;
  box-shadow: 0 0 0 0 rgba(91,180,138,0.5); }
@keyframes live-pulse {
  0% { box-shadow: 0 0 0 0 rgba(91,180,138,0.5); }
  70% { box-shadow: 0 0 0 8px rgba(91,180,138,0); }
  100% { box-shadow: 0 0 0 0 rgba(91,180,138,0); }
}

.pills {
  display: flex; gap: 6px; margin-top: 10px;
  overflow-x: auto; -webkit-overflow-scrolling: touch;
  padding-bottom: 2px; scrollbar-width: none;
}
.pills::-webkit-scrollbar { display: none; }
.pill {
  flex: 0 0 auto;
  display: inline-flex; align-items: center; gap: 5px;
  background: transparent; color: var(--ink-soft);
  border: 1px solid rgba(87,116,133,0.25);
  border-radius: 999px; padding: 5px 12px;
  font: inherit; font-size: 12px; font-weight: 600;
  letter-spacing: -0.005em; cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: all 0.15s ease;
  font-family: var(--font-mono);
}
.pill:hover { color: var(--ink); border-color: var(--ink-soft); }
.pill.active, .pill.is-active {
  background: var(--ink); color: var(--paper); border-color: var(--ink);
}
.pill.nav, .pill--nav {
  background: rgba(232,137,94,0.12); color: var(--accent);
  border-color: transparent; font-family: var(--font-sans);
}
.pill.nav-first { margin-left: auto; }

/* ── Hero strip ────────────────────────────────────────── */
.hero { padding: 14px var(--pad) 4px; }
.hero-stack { display: grid; grid-template-columns: 1fr; gap: 10px; }
@media (min-width: 720px) { .hero-stack { grid-template-columns: repeat(3, 1fr); } }
.hero-card {
  position: relative;
  display: grid; grid-template-columns: 1fr auto;
  align-items: center; gap: 12px;
  background: var(--card); border-radius: 18px;
  padding: 14px 16px 14px 18px;
  box-shadow:
    0 1px 0 rgba(0,0,0,0.02),
    0 8px 24px -16px rgba(232,137,94,0.5),
    inset 0 0 0 1px rgba(232,137,94,0.18);
  overflow: hidden; isolation: isolate;
  transition: transform 0.18s ease;
}
.hero-card:active { transform: scale(0.992); }
.hero-card::before {
  content: ""; position: absolute; inset: 0;
  background: radial-gradient(220px 120px at 0% 100%, var(--c, var(--accent)) 0%, transparent 70%);
  opacity: 0.22; pointer-events: none; z-index: -1;
}
.hero-card__title {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 700; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--c, var(--accent));
  grid-column: 1 / -1;
}
.hero-card__now {
  margin-left: auto; font-family: var(--font-mono);
  font-size: 10px; letter-spacing: 0.06em;
  color: var(--mute); text-transform: lowercase;
}
.hero-card__name {
  font-weight: 700; font-size: 20px; line-height: 1.1;
  color: var(--ink); letter-spacing: -0.015em;
}
.hero-card__reason {
  margin-top: 2px; font-size: 12px; color: var(--ink-soft);
}
.hero-card__arc { grid-row: 2 / span 2; grid-column: 2;
  align-self: center; justify-self: end; }
.hero-card__shimmer {
  position: absolute; inset: 0;
  background: linear-gradient(110deg, transparent 30%,
    rgba(232,137,94,0.14) 50%, transparent 70%);
  background-size: 250% 100%;
  pointer-events: none; z-index: -1;
  animation: shimmer 6s ease-in-out infinite;
}
@keyframes shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}

/* ── Alert banner ──────────────────────────────────────── */
.alert-banner {
  background: rgba(212,74,42,0.10);
  border-bottom: 1px solid rgba(212,74,42,0.25);
  padding: 10px var(--pad); font-size: 13px; color: var(--bad);
  display: flex; gap: 8px; align-items: center;
}
.alert-banner .ev { color: var(--ink); font-weight: 700; }
.alert-banner .area {
  color: var(--mute); font-size: 10px;
  font-family: var(--font-mono); letter-spacing: 0.06em;
}

/* ── Feed (cards grid) ────────────────────────────────── */
main.feed {
  padding: 14px var(--pad);
  display: grid; gap: 14px;
  grid-template-columns: 1fr;
}
@media (min-width: 720px) { main.feed { grid-template-columns: repeat(2, 1fr); gap: 16px; padding: 16px; } }
@media (min-width: 1100px) { main.feed { grid-template-columns: repeat(3, 1fr); max-width: 1400px; margin: 0 auto; } }

/* ── Beach card ───────────────────────────────────────── */
.card {
  background: var(--card); border-radius: 22px;
  padding: 16px 16px 14px;
  display: flex; flex-direction: column; gap: 14px;
  box-shadow:
    0 1px 0 rgba(0,0,0,0.02),
    0 12px 30px -22px rgba(31,63,77,0.35),
    inset 0 0 0 1px rgba(230,220,200,0.6);
}
.card-h {
  display: grid; grid-template-columns: 1fr auto;
  gap: 14px; align-items: flex-start;
}
.card-h-l { min-width: 0; }
.card-name {
  font-weight: 700; font-size: 20px; line-height: 1.1;
  margin: 0; color: var(--ink); letter-spacing: -0.015em;
}
.card-meta {
  display: flex; flex-wrap: wrap; align-items: center;
  gap: 6px; margin-top: 6px;
}
.card-posto {
  display: inline-flex; align-items: center; gap: 3px;
  font-family: var(--font-mono); font-size: 11px;
  letter-spacing: 0.02em; color: var(--ink-soft);
}
.card-state {
  font-family: var(--font-mono);
  font-size: 10px; letter-spacing: 0.08em;
  color: var(--ink); background: var(--paper-warm);
  border: 1px solid var(--line);
  padding: 2px 6px; border-radius: 4px;
}
.badge {
  font-size: 10px; font-weight: 600; letter-spacing: -0.005em;
  color: var(--ink-soft);
  background: rgba(87,116,133,0.10);
  padding: 3px 8px; border-radius: 999px;
  white-space: nowrap;
}
.badge--surf { color: var(--surf); background: rgba(232,137,94,0.12); }
.badge--swim { color: var(--swim); background: rgba(90,159,181,0.14); }
.badge--warm { color: var(--bad);  background: rgba(212,74,42,0.10); }

/* Live cam thumbnail */
.card-cam {
  position: relative; width: 78px; height: 78px;
  border-radius: 14px; overflow: hidden;
  background: #d8d2c1; flex: 0 0 78px;
  isolation: isolate;
}
.card-cam img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.card-cam-dot {
  position: absolute; top: 7px; left: 7px;
  width: 8px; height: 8px; border-radius: 50%;
  background: #ff5b5b;
  box-shadow: 0 0 0 2px rgba(255,255,255,0.6);
  animation: live-pulse 2s infinite;
  z-index: 1;
}
.card-cam-tag {
  position: absolute; bottom: 5px; left: 5px;
  font-family: var(--font-mono);
  font-size: 9px; letter-spacing: 0.06em;
  color: white; background: rgba(0,0,0,0.55);
  padding: 2px 5px; border-radius: 4px;
  text-transform: uppercase;
}
.card-cam--off {
  background: var(--paper-warm);
  display: grid; place-items: center;
}
.card-cam-off-text {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.06em; color: var(--mute); text-transform: uppercase;
}

/* ── Score row (sun-arc dials) ─────────────────────────── */
.score-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; padding: 4px 0 0; }
.sa { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.sa-label {
  font-size: 11px; font-weight: 600;
  color: var(--ink-soft); letter-spacing: -0.005em;
  text-align: center;
}

/* ── Hourly strip ──────────────────────────────────────── */
.hs {
  display: flex; flex-direction: column; gap: 6px;
  padding: 10px 0;
  border-top: 1px dashed rgba(230,220,200,0.9);
  border-bottom: 1px dashed rgba(230,220,200,0.9);
}
.hs-axis {
  display: flex; justify-content: space-between;
  padding: 0 60px 4px 80px;
  font-family: var(--font-mono);
  font-size: 9px; letter-spacing: 0.06em;
  color: var(--mute); text-transform: uppercase;
}
.hs-row {
  display: grid; grid-template-columns: 76px 1fr 50px;
  align-items: center; gap: 6px;
}
.hs-label {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 600; color: var(--ink-soft);
}
.hs-bars {
  position: relative;
  display: grid; grid-template-columns: repeat(24, 1fr);
  align-items: flex-end; gap: 1px;
  height: 26px; padding-bottom: 2px;
}
.hs-bar {
  height: var(--h, 2px);
  background: color-mix(in oklab, var(--c, var(--ink-soft)) 35%, transparent);
  border-radius: 1.5px; align-self: end;
}
.hs-bar.in-win { background: var(--c, var(--ink-soft)); }
.hs-bar.is-now {
  background: var(--c, var(--ink-soft));
  box-shadow: 0 0 0 1.5px rgba(31,63,77,0.18);
  position: relative; z-index: 1;
}
.hs-now-line {
  position: absolute; top: -2px; bottom: 0;
  width: 1.5px; background: var(--ink);
  transform: translateX(-50%); opacity: 0.5;
  pointer-events: none;
}
.hs-window-underline {
  position: absolute; bottom: -3px;
  height: 2px; border-radius: 1px; opacity: 0.7;
}
.hs-window-label {
  font-family: var(--font-mono);
  font-size: 10px; font-weight: 600;
  letter-spacing: 0.02em; text-align: right;
  font-variant-numeric: tabular-nums;
}

/* ── Best window pill ──────────────────────────────────── */
.bw {
  position: relative;
  display: grid; grid-template-columns: auto 1fr auto;
  gap: 10px; align-items: center;
  padding: 10px 12px;
  background: color-mix(in oklab, var(--bw-c, var(--accent)) 8%, var(--paper-warm));
  border-radius: 12px;
}
.bw-bar {
  width: 3px; min-height: 22px;
  background: var(--bw-c, var(--accent));
  border-radius: 2px; align-self: stretch;
}
.bw-text { font-size: 13px; color: var(--ink); font-weight: 500; }
.bw-window {
  font-family: var(--font-mono); font-size: 11px;
  letter-spacing: 0.04em; color: var(--bw-c, var(--accent));
  background: var(--card); padding: 4px 8px;
  border-radius: 999px; font-weight: 600; white-space: nowrap;
}

/* ── Conditions row ────────────────────────────────────── */
.cond {
  display: grid; grid-template-columns: repeat(4, 1fr);
  border-top: 1px dashed rgba(230,220,200,0.85);
  padding-top: 12px;
}
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
.cond-v small {
  font-weight: 500; font-size: 10px;
  color: var(--ink-soft); margin-left: 1px;
}
.cond-l {
  font-size: 10px; font-weight: 500;
  color: var(--ink-soft); letter-spacing: 0.02em;
}

/* ── Card footer ───────────────────────────────────────── */
.card-f {
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px; padding-top: 10px;
  border-top: 1px solid rgba(230,220,200,0.6);
}
.crowd { display: flex; align-items: center; gap: 10px; }
.crowd-parasols { display: inline-flex; gap: 2px; }
.crowd-meta { display: flex; align-items: baseline; gap: 0; font-size: 12px; }
.crowd-label { font-weight: 700; color: var(--ink); text-transform: lowercase; }
.crowd-peak { color: var(--mute); font-size: 11px; margin-left: 4px; }
.crowd-peak em { font-style: normal; color: var(--ink-soft); font-weight: 600; }
.card-cta {
  display: inline-flex; align-items: center; gap: 3px;
  font-size: 12px; font-weight: 700; letter-spacing: -0.005em;
  color: var(--accent); padding: 4px 6px;
  border-radius: 8px; transition: background 0.15s;
}
.card-cta:hover { background: rgba(232,137,94,0.10); }

/* ── Ad slot ───────────────────────────────────────────── */
.ad-slot {
  grid-column: 1 / -1;
  display: flex; flex-direction: column; gap: 4px;
  border: 1px dashed rgba(148,168,180,0.5);
  border-radius: 14px; padding: 8px 12px;
  background: var(--paper-warm);
  text-align: center;
}
.ad-slot-tag {
  font-family: var(--font-mono);
  font-size: 9px; letter-spacing: 0.08em;
  color: var(--mute); text-transform: uppercase;
  text-align: left;
}
.ad-slot iframe { max-width: 600px; margin: 0 auto; background: transparent; }

/* ── Footer ────────────────────────────────────────────── */
.footer {
  text-align: center; padding: 24px var(--pad) 28px;
  color: var(--mute); font-size: 11px;
  font-family: var(--font-mono); letter-spacing: 0.02em;
}
"""


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    postos = json.load(open(DATA))
    for p in postos:
        p["_surf"]  = surf_score(p)
        p["_swim"]  = swim_score(p)
        p["_sun"]   = sun_score(p)
        p["_shade"] = shade_score(p)
        p["_hourly"] = hourly_scores(p)

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
        "surf": surf_w["id"], "swim": swim_w["id"], "sun": sun_w["id"],
        "warmest": warmest["id"],
        "max_wave": argmax("surf.wave_height_m"),
        "min_wave": argmin("surf.wave_height_m"),
        "max_seatemp": argmax("water.sea_temp_c"),
        "max_wind": argmax("weather.wind_kmh"),
        "min_wind": argmin("weather.wind_kmh"),
    }

    postos_sorted = sorted(postos, key=lambda p: -p["_surf"])
    agito_data = load_optional(AGITO)
    now_hour = datetime.now().hour
    card_list = [render_card(p, marks, agito_data, now_hour) for p in postos_sorted]
    cards = insert_ads(card_list)

    ts = datetime.fromtimestamp(postos[0]["fetched_at"]).strftime("%H:%M")
    sample = postos[0]
    aqi_text, _ = aqi_label(sample["air"]["aqi"])
    uv_avg = round(sum(p["weather"]["uv"] or 0 for p in postos) / len(postos), 1)
    cloud_avg = round(sum(p["weather"]["cloud_pct"] or 0 for p in postos) / len(postos))
    region_count = len({p["beach"] for p in postos})
    region_label = "Brasil" if region_count > 1 else postos[0]["beach"].split()[0]

    # Alerts
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

    # Hero
    def why_surf(p):
        return f"onda {fmt(p['surf']['wave_height_m'], 'm')} · {fmt(p['surf']['wave_period_s'], 's', 0)} período"
    def why_swim(p):
        return f"onda {fmt(p['surf']['wave_height_m'], 'm')} · água {fmt(p['water']['sea_temp_c'], '°', 0)}"
    def why_sun(p):
        return f"nuvens {fmt(p['weather']['cloud_pct'], '%', 0)} · uv {fmt(p['weather']['uv'], '', 0)}"

    hero_html = (
        render_hero_card("surf", "bom pra surfar", "surfar", "var(--surf)",
                         surf_w, why_surf(surf_w), surf_w["_surf"])
        + render_hero_card("swim", "bom pra nadar", "nadar", "var(--swim)",
                           swim_w, why_swim(swim_w), swim_w["_swim"])
        + render_hero_card("sun", "bom pro sol", "sol", "var(--sun)",
                           sun_w, why_sun(sun_w), sun_w["_sun"])
    )

    states = sorted({p["state"] for p in postos if p.get("state")})
    state_pills = (
        '<button class="pill active" data-st="all">todas</button>'
        + "".join(f'<button class="pill" data-st="{s}">{s}</button>' for s in states)
        + '<a class="pill nav nav-first" href="melhores.html">melhores</a>'
        + '<a class="pill nav" href="sobre.html">sobre</a>'
    )

    wordmark = ('<div class="wordmark">'
                '<span class="wm-praia">praia</span>'
                '<span class="wm-smart">smart</span>'
                '</div>')

    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#F4EFE4">
<title>praia smart — {region_label} agora</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="topbar">
  <div class="topbar-row1">
    {wordmark}
  </div>
  <div class="pills">{state_pills}</div>
</header>
{alert_banner}
<section class="hero"><div class="hero-stack">{hero_html}</div></section>
<main class="feed" id="grid">
{cards}
</main>
<div class="footer">dados Open-Meteo · câmeras YouTube · v0.4</div>
<script>
(()=>{{
  const pills = document.querySelectorAll('.pill[data-st]');
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
