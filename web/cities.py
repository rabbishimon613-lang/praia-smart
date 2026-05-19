"""Weekly auto-generated city "fim de semana" pages.

Reads data/conditions.json, groups the 12 beaches by city, and writes
web/<city-slug>/fim-de-semana.html for each of the 10 cities. Designed
to match Friday-afternoon searches: "rio fim de semana", "praias santos
sabado", "natal previsao fim de semana".

Runs after web/detail.py in the build pipeline. Refreshes every 15 min
with the rest of the site — same freshness signal Google likes.
"""
import json
import os
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import (
    surf_score, swim_score, shade_score,
    render_agua_box, _BALNE_BY_BEACH,
    AD_HTML,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "conditions.json")
OUT_ROOT = os.path.join(ROOT, "web")
SITE_URL = "https://praiasmart.com"

# ─────────────────────────────────────────────────────────────
# City registry — slug → (display name, state, beach ids, blurb)
# Order also defines homepage pill row and sitemap order.
# ─────────────────────────────────────────────────────────────

CITIES = [
    ("rio", "Rio de Janeiro", "RJ",
     ["copa-p5", "leblon-mirante", "sao-conrado"],
     "As praias do Rio formam um arco quase contínuo do Leme ao Recreio, com cada trecho "
     "tendo personalidade própria: Copacabana mais democrática, Leblon mais família, São "
     "Conrado com surf consistente e parapente vindo da Pedra Bonita. O mar é frio quando "
     "o vento vira sul e morno quando entra norte. Balneabilidade muda rápido depois de "
     "chuva — vale checar antes de mergulhar.",
     ["floripa", "cabo-frio", "santos"]),

    ("cabo-frio", "Cabo Frio", "RJ",
     ["cabo-frio-forte"],
     "Cabo Frio é o coração da Região dos Lagos: areia branca e fininha, água verde puxando "
     "pra turquesa e a famosa ressurgência que sopra água gelada mesmo em pleno verão. A Praia "
     "do Forte, no canto do canal do Itajuru, é cartão-postal e ponto de encontro. Cidade "
     "boa pra ficar uns dias, com Búzios e Arraial logo ao lado.",
     ["rio", "santos", "morro-de-sao-paulo"]),

    ("morro-de-sao-paulo", "Morro de São Paulo", "BA",
     ["morro-terceira"],
     "Morro de São Paulo, na Ilha de Tinharé, é praia sem carro: tudo se faz a pé ou de "
     "trator. As quatro praias se sucedem da Primeira (com tirolesa) até a Quarta (sossego "
     "total), com a Terceira sendo a mais procurada por famílias — piscinas naturais na maré "
     "baixa e barracas com moqueca. Água quente o ano todo, ondas calmas, brisa nordeste.",
     ["natal", "cabo-frio", "rio"]),

    ("santos", "Santos", "SP",
     ["santos-gonzaga"],
     "Santos tem o maior jardim de orla do mundo e uma faixa de areia larguíssima dividida "
     "em canais — Gonzaga, no Canal 2, é o trecho mais clássico, com prédios históricos, "
     "calçadão movimentado e quiosques. O mar costuma ser calmo, bom pra banho de família, "
     "e a balneabilidade melhorou bastante nos últimos anos. Vento entra forte à tarde.",
     ["guaruja", "praia-grande", "rio"]),

    ("guaruja", "Guarujá", "SP",
     ["guaruja-enseada"],
     "A Enseada, no Guarujá, é a maior praia da cidade e a mais frequentada por paulistanos: "
     "areia larga, mar com ondas curtas, hotéis e prédios à beira-mar. O Posto 11 fica num "
     "trecho mais tranquilo, longe da agitação do centro da Enseada. Bom pra criança em maré "
     "baixa, vento sul à tarde aumenta a arrebentação.",
     ["santos", "praia-grande", "rio"]),

    ("praia-grande", "Praia Grande", "SP",
     ["praia-grande-boqueirao"],
     "Praia Grande tem 22 quilômetros de praia contínua dividida em bairros — Boqueirão é "
     "um dos mais procurados, com calçadão renovado, quiosques e estacionamento fácil. Mar "
     "raso por bons metros, ideal pra banho com criança, e ondas pequenas que servem pra "
     "iniciante de surf. Vento sudoeste à tarde.",
     ["santos", "guaruja", "rio"]),

    ("balneario-camboriu", "Balneário Camboriú", "SC",
     ["balneario-camboriu"],
     "Balneário Camboriú é a praia urbana mais verticalizada do Brasil: prédios altíssimos "
     "encostados na areia, calçadão movimentado e Avenida Atlântica com vida noturna intensa "
     "no verão. A Praia Central tem mar formado, ondas que servem pra surf iniciante a "
     "intermediário, e areia quase sempre cheia entre dezembro e fevereiro.",
     ["floripa", "balneario-rincao", "guaruja"]),

    ("floripa", "Florianópolis", "SC",
     ["floripa-barra-lagoa"],
     "Florianópolis tem mais de 40 praias na ilha, cada uma com um caráter — da Barra da "
     "Lagoa, com canal e vila de pescadores, até Joaquina, Mole e Praia do Santinho. Mar "
     "geralmente mais limpo que no Sudeste, água fria no verão por causa de ressurgências, "
     "vento sul forte que dura dias.",
     ["balneario-camboriu", "balneario-rincao", "rio"]),

    ("balneario-rincao", "Balneário Rincão", "SC",
     ["balneario-rincao"],
     "Balneário Rincão é praia do extremo sul catarinense, ainda preservada do turismo de "
     "massa: orla longa, areia clara e dunas em alguns trechos. Mar aberto com ondas "
     "constantes — bom pra surf — e vento sudeste quase sempre presente. Cidade pequena, "
     "ideal pra quem busca sossego e visual de fim de mundo.",
     ["floripa", "balneario-camboriu", "guaruja"]),

    ("natal", "Natal", "RN",
     ["natal-ponta-negra"],
     "Ponta Negra é a praia mais famosa de Natal: três quilômetros de areia com o Morro do "
     "Careca no canto sul, duna gigante coberta por vegetação que se tornou símbolo da "
     "cidade. Água quente o ano todo, vento alísio constante, mar com ondas pequenas "
     "boas pra banho. Calçadão e quiosques no trecho central.",
     ["morro-de-sao-paulo", "cabo-frio", "rio"]),
]

CITY_BY_SLUG = {c[0]: c for c in CITIES}

# Map of beach id → city slug
BEACH_TO_CITY = {bid: c[0] for c in CITIES for bid in c[3]}


# ─────────────────────────────────────────────────────────────
# Date helpers (PT-BR weekend window)
# ─────────────────────────────────────────────────────────────

PT_MONTHS = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


def weekend_window(today=None):
    """Return (start_date, end_date, pt_label) for the upcoming weekend.

    If today is Mon-Thu: next Sat-Sun.
    If Fri: Fri-Sun (include today).
    If Sat: Sat-Sun.
    If Sun: just Sun.
    """
    today = today or date.today()
    wd = today.weekday()  # Mon=0 .. Sun=6
    if wd <= 3:           # Mon-Thu
        start = today + timedelta(days=(5 - wd))
        end = start + timedelta(days=1)
    elif wd == 4:         # Fri
        start = today
        end = today + timedelta(days=2)
    elif wd == 5:         # Sat
        start = today
        end = today + timedelta(days=1)
    else:                 # Sun
        start = today
        end = today

    if start == end:
        label = f"{start.day} de {PT_MONTHS[start.month - 1]}"
    elif start.month == end.month:
        label = f"{start.day} a {end.day} de {PT_MONTHS[start.month - 1]}"
    else:
        label = (f"{start.day} de {PT_MONTHS[start.month - 1]} a "
                 f"{end.day} de {PT_MONTHS[end.month - 1]}")
    return start, end, label


# ─────────────────────────────────────────────────────────────
# Scoring helpers
# ─────────────────────────────────────────────────────────────

def family_score(p):
    """Composite: warm water + low waves + low UV at midday."""
    sea_t = (p.get("water") or {}).get("sea_temp_c") or 0
    h = (p.get("surf") or {}).get("wave_height_m") or 0
    uv = (p.get("weather") or {}).get("uv") or 0
    warmth = max(0, min((sea_t - 18) / 12, 1.0))
    calm = 1 / (1 + h * 1.5)
    uv_ok = max(0, 1 - max(0, uv - 5) / 6)
    return round(warmth * 0.35 + calm * 0.4 + uv_ok * 0.25, 3)


def _hour_of(iso):
    try:
        return int(iso[11:13])
    except Exception:
        return 0


def _date_of(iso):
    try:
        return iso[:10]
    except Exception:
        return ""


def _avg(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def day_summary(p, day_iso):
    """One-line PT-BR summary for a given calendar date based on hourly arrays."""
    h = p.get("hourly") or {}
    times = h.get("time") or []
    waves = h.get("wave_m") or []
    winds = h.get("wind_kmh") or []
    uvs = h.get("uv") or []
    precs = h.get("precip_mm") or []

    morning, afternoon = {"w": [], "wd": [], "uv": [], "pr": []}, {"w": [], "wd": [], "uv": [], "pr": []}
    for i, t in enumerate(times):
        if _date_of(t) != day_iso:
            continue
        hod = _hour_of(t)
        bucket = morning if 6 <= hod < 12 else (afternoon if 12 <= hod < 18 else None)
        if bucket is None:
            continue
        if i < len(waves): bucket["w"].append(waves[i])
        if i < len(winds): bucket["wd"].append(winds[i])
        if i < len(uvs): bucket["uv"].append(uvs[i])
        if i < len(precs): bucket["pr"].append(precs[i])

    def describe(b, period):
        if not (b["w"] or b["wd"] or b["uv"]):
            return None
        w = _avg(b["w"]) or 0
        wd = _avg(b["wd"]) or 0
        uv = _avg(b["uv"]) or 0
        pr = sum([x for x in b["pr"] if x is not None]) if b["pr"] else 0
        if pr >= 2:
            mood = "chuva"
        elif wd >= 25:
            mood = "vento forte"
        elif w >= 1.6:
            mood = "mar mexido"
        elif uv >= 9 and period == "tarde":
            mood = "sol forte"
        elif uv < 1 and period == "manhã":
            mood = "nublado cedo"
        elif w < 0.6 and wd < 12:
            mood = "tudo calmo"
        else:
            mood = "boa"
        return f"{period} {mood}"

    parts = [x for x in (describe(morning, "manhã"), describe(afternoon, "tarde")) if x]
    return ", ".join(parts) if parts else "sem previsão horária"


def mini_strip(p, day_iso, color="var(--swim)"):
    """Tiny 12-bar strip 6h-18h for a single day, swim score by default."""
    h = p.get("hourly") or {}
    times = h.get("time") or []
    waves = h.get("wave_m") or []
    uvs = h.get("uv") or []
    sea_t = (p.get("water") or {}).get("sea_temp_c") or 0

    bars = []
    for hod in range(6, 19):
        score = 0.0
        for i, t in enumerate(times):
            if _date_of(t) == day_iso and _hour_of(t) == hod:
                wv = waves[i] if i < len(waves) and waves[i] is not None else 0
                uv = uvs[i] if i < len(uvs) and uvs[i] is not None else 0
                calm = 1 / (1 + wv)
                warmth = max(0, min((sea_t - 18) / 12, 1.0))
                score = (calm * 0.6 + warmth * 0.4) * (1.0 if uv > 0 else 0.25)
                break
        h_px = max(3, int(score * 22))
        bars.append(
            f'<span class="ms-bar" style="height:{h_px}px;background:{color}"></span>'
        )
    return f'<div class="ms-strip">{"".join(bars)}</div>'


# ─────────────────────────────────────────────────────────────
# Cam thumbnail
# ─────────────────────────────────────────────────────────────

def cam_thumb(p):
    yt = p.get("youtube_id")
    if not yt:
        return '<div class="thumb thumb--off">sem cam</div>'
    return (
        f'<a class="thumb" href="../beach/{p["id"]}.html" aria-label="ver cam ao vivo">'
        f'<img src="https://img.youtube.com/vi/{yt}/mqdefault.jpg" alt="" loading="lazy">'
        f'<span class="thumb-dot"></span>'
        f'</a>'
    )


# ─────────────────────────────────────────────────────────────
# CSS (minimal additions on top of base tokens)
# ─────────────────────────────────────────────────────────────

CSS = """
:root {
  --paper:#F4EFE4; --paper-warm:#F9F4E8; --card:#FFFFFF;
  --ink:#1F3F4D; --ink-soft:#577485; --mute:#94A8B4;
  --line:#E6DCC8;
  --accent:#E8895E; --surf:#E8895E; --swim:#5A9FB5; --sun:#E5B86A; --shade:#7C9183;
  --good:#5BB48A; --ok:#5A9FB5; --warn:#E5B86A; --bad:#D44A2A;
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
.wordmark { display: inline-flex; align-items: baseline; gap: 4px; }
.wordmark .wm-praia {
  font-family: var(--font-serif); font-style: italic; font-weight: 400;
  font-size: 28px; color: var(--accent); line-height: 1;
}
.wordmark .wm-smart {
  font-family: var(--font-sans); font-weight: 700;
  font-size: 17px; color: var(--ink); letter-spacing: -0.005em;
}
.topbar-title { flex: 1; min-width: 0; }
.topbar-title h1 {
  margin: 0; font-size: 16px; font-weight: 700;
  letter-spacing: -0.015em; color: var(--ink);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.topbar-meta {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.06em; color: var(--ink-soft);
  text-transform: uppercase; margin-top: 2px;
}

main { padding: 16px var(--pad) 40px; max-width: 760px; margin: 0 auto; }

.intro {
  margin: 20px 0 24px;
}
.intro h2 {
  font-family: var(--font-serif); font-style: italic; font-weight: 400;
  font-size: 38px; line-height: 1.05; color: var(--ink);
  margin: 0 0 12px; letter-spacing: -0.015em;
}
.intro p {
  margin: 0; font-size: 15px; color: var(--ink-soft);
  max-width: 56ch;
}

.section-tag {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.08em; color: var(--ink-soft);
  text-transform: uppercase; margin: 28px 0 10px;
}

.picks { display: grid; grid-template-columns: 1fr; gap: 10px; }
@media (min-width: 640px) { .picks { grid-template-columns: repeat(3, 1fr); } }
.pick {
  background: var(--card); border-radius: 16px;
  padding: 14px 16px; border: 1px solid var(--line);
  position: relative; overflow: hidden;
  box-shadow: 0 8px 24px -18px rgba(31,63,77,0.35);
}
.pick::before {
  content: ""; position: absolute; inset: 0;
  background: radial-gradient(180px 100px at 0% 100%, var(--pc, var(--accent)) 0%, transparent 70%);
  opacity: 0.18; pointer-events: none;
}
.pick-label {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.08em; color: var(--pc, var(--accent));
  text-transform: uppercase; font-weight: 700;
}
.pick-name {
  font-size: 19px; font-weight: 700; color: var(--ink);
  margin-top: 4px; letter-spacing: -0.01em;
}
.pick-why {
  font-size: 12px; color: var(--ink-soft); margin-top: 4px;
}
.pick a.pick-link {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.06em; color: var(--ink);
  display: inline-block; margin-top: 8px;
  border-bottom: 1px solid var(--ink-soft);
}

.beach-card {
  background: var(--card); border-radius: 18px;
  border: 1px solid var(--line);
  padding: 14px 16px; margin: 10px 0;
  display: grid; grid-template-columns: 1fr 96px;
  gap: 12px; align-items: start;
  box-shadow: 0 8px 24px -20px rgba(31,63,77,0.35);
}
.beach-card h3 {
  margin: 0; font-size: 17px; font-weight: 700;
  letter-spacing: -0.01em; color: var(--ink);
}
.beach-card .state-tag {
  font-family: var(--font-mono); font-size: 10px;
  color: var(--ink-soft); letter-spacing: 0.06em;
  text-transform: uppercase; margin-left: 6px;
}
.day-row {
  display: grid; grid-template-columns: 38px 1fr;
  gap: 8px; align-items: center; margin-top: 10px;
}
.day-label {
  font-family: var(--font-mono); font-size: 10px;
  color: var(--ink-soft); letter-spacing: 0.05em;
  text-transform: uppercase; font-weight: 700;
}
.day-summary {
  font-size: 12px; color: var(--ink-soft);
}
.ms-strip {
  display: inline-flex; align-items: flex-end; gap: 2px;
  height: 24px; margin-right: 8px; vertical-align: middle;
}
.ms-bar { width: 4px; border-radius: 2px; opacity: 0.85; display: inline-block; }

.agua-mini {
  font-family: var(--font-mono); font-size: 11px;
  letter-spacing: 0.04em; margin-top: 10px;
  color: var(--ink-soft); text-transform: uppercase;
}
.agua-mini .agua-pill {
  display: inline-block; padding: 2px 8px; border-radius: 999px;
  font-weight: 700; color: var(--am-c, var(--ink));
  background: color-mix(in srgb, var(--am-c, var(--accent)) 14%, transparent);
  margin-right: 6px;
}

.beach-card a.see-more {
  font-family: var(--font-mono); font-size: 11px;
  letter-spacing: 0.04em; color: var(--accent);
  display: inline-block; margin-top: 10px;
  border-bottom: 1px solid color-mix(in srgb, var(--accent) 40%, transparent);
}

.thumb {
  display: block; width: 96px; aspect-ratio: 16/10;
  border-radius: 12px; overflow: hidden;
  position: relative; background: #0a1620;
}
.thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.thumb--off {
  display: grid; place-items: center; color: var(--mute);
  font-family: var(--font-mono); font-size: 9px;
  letter-spacing: 0.06em; text-transform: uppercase;
}
.thumb-dot {
  position: absolute; top: 6px; right: 6px;
  width: 6px; height: 6px; border-radius: 50%;
  background: #ff5b5b;
  box-shadow: 0 0 0 0 rgba(255,91,91,0.6);
  animation: ph 2s infinite;
}
@keyframes ph {
  0% { box-shadow: 0 0 0 0 rgba(255,91,91,0.6); }
  70% { box-shadow: 0 0 0 6px rgba(255,91,91,0); }
}

.about {
  background: var(--paper-warm); border-radius: 18px;
  padding: 18px 20px; margin: 24px 0;
  border: 1px solid var(--line);
}
.about h3 {
  font-family: var(--font-serif); font-style: italic; font-weight: 400;
  font-size: 24px; margin: 0 0 8px; color: var(--ink);
}
.about p { margin: 0; color: var(--ink-soft); font-size: 14px; }

.crosslinks {
  margin: 30px 0 12px;
  font-family: var(--font-mono); font-size: 11px;
  color: var(--ink-soft); letter-spacing: 0.04em;
}
.crosslinks a {
  display: inline-block; padding: 6px 12px; border-radius: 999px;
  background: var(--card); border: 1px solid var(--line);
  color: var(--ink); margin: 4px 6px 4px 0;
  text-transform: none; letter-spacing: -0.005em;
  font-family: var(--font-sans); font-weight: 600;
}
.crosslinks a:hover { border-color: var(--accent); color: var(--accent); }

.footer {
  text-align: center; margin: 32px 0 16px;
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.08em; color: var(--mute);
  text-transform: uppercase;
}

/* Agua-box reuse */
.agua-box {
  background: var(--card); border-radius: 16px;
  border: 1px solid var(--line); padding: 12px 14px;
  margin-top: 10px;
}
.agua-status { font-weight: 700; font-size: 16px; }
.agua-meta {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.06em; color: var(--ink-soft);
  text-transform: uppercase; margin-top: 2px;
}
"""


# ─────────────────────────────────────────────────────────────
# Agua status mini-pill (compact version for the city page)
# ─────────────────────────────────────────────────────────────

_STATUS_PILL = {
    "propria":     ("própria",      "var(--good)"),
    "impropria":   ("imprópria",    "var(--bad)"),
    "alerta":      ("em alerta",    "var(--warn)"),
    "sem_dados":   ("sem boletim",  "var(--mute)"),
}


def agua_pill(beach_id):
    entry = _BALNE_BY_BEACH.get(beach_id) or {}
    status = entry.get("status") or "sem_dados"
    label, color = _STATUS_PILL.get(status, _STATUS_PILL["sem_dados"])
    src = entry.get("source") or "INEA"
    rd = entry.get("report_date")
    when = ""
    if rd:
        try:
            d = datetime.strptime(rd, "%Y-%m-%d").date()
            days = (date.today() - d).days
            when = " · hoje" if days <= 0 else (" · ontem" if days == 1 else f" · {days}d")
        except Exception:
            pass
    return (
        f'<div class="agua-mini" style="--am-c:{color}">'
        f'<span class="agua-pill">{label}</span>'
        f'água · {src}{when}'
        f'</div>'
    )


# ─────────────────────────────────────────────────────────────
# Renderers
# ─────────────────────────────────────────────────────────────

def render_pick(label, beach, why, color_var):
    return (
        f'<div class="pick" style="--pc:{color_var}">'
        f'<div class="pick-label">{label}</div>'
        f'<div class="pick-name">{beach["beach"]}</div>'
        f'<div class="pick-why">{why}</div>'
        f'<a class="pick-link" href="../beach/{beach["id"]}.html">ver detalhes →</a>'
        f'</div>'
    )


def render_beach_card(p, days):
    """days = [(label, iso_date), ...] up to 2."""
    rows = []
    for label, iso in days:
        strip = mini_strip(p, iso)
        summary = day_summary(p, iso)
        rows.append(
            f'<div class="day-row">'
            f'<div class="day-label">{label}</div>'
            f'<div>{strip}<span class="day-summary">{summary}</span></div>'
            f'</div>'
        )
    return (
        f'<article class="beach-card">'
        f'<div>'
        f'<h3>{p["beach"]} <span class="state-tag">{p.get("posto","")} · {p["state"]}</span></h3>'
        f'{"".join(rows)}'
        f'{agua_pill(p["id"])}'
        f'<a class="see-more" href="../beach/{p["id"]}.html">ver detalhes →</a>'
        f'</div>'
        f'{cam_thumb(p)}'
        f'</article>'
    )


def render_picks(beaches):
    """3 picks: surf, swim, family."""
    if not beaches:
        return ""
    surf_b = max(beaches, key=lambda p: p.get("_surf", 0))
    swim_b = max(beaches, key=lambda p: p.get("_swim", 0))
    fam_b = max(beaches, key=lambda p: p.get("_family", 0))

    def reason(p, kind):
        w = p.get("weather") or {}; s = p.get("surf") or {}; a = p.get("water") or {}
        wave = s.get("wave_height_m")
        wind = w.get("wind_kmh")
        sea = a.get("sea_temp_c")
        if kind == "surf":
            bits = []
            if wave is not None: bits.append(f"onda {wave:.1f}m")
            if wind is not None: bits.append(f"vento {int(wind)}km/h")
            return ", ".join(bits) or "melhor combo da cidade"
        if kind == "swim":
            bits = []
            if wave is not None: bits.append(f"mar {wave:.1f}m")
            if sea is not None: bits.append(f"água {sea:.0f}°C")
            return ", ".join(bits) or "mar mais calmo"
        bits = []
        if sea is not None: bits.append(f"água {sea:.0f}°C")
        if wave is not None: bits.append(f"onda {wave:.1f}m")
        return ", ".join(bits) or "tranquilo pra família"

    return (
        f'<div class="picks">'
        f'{render_pick("Pra surfar", surf_b, reason(surf_b, "surf"), "var(--surf)")}'
        f'{render_pick("Pra nadar", swim_b, reason(swim_b, "swim"), "var(--swim)")}'
        f'{render_pick("Pra família", fam_b, reason(fam_b, "family"), "var(--good)")}'
        f'</div>'
    )


# ─────────────────────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────────────────────

def render_city_page(slug, city_name, state, beaches, blurb, related):
    start, end, label = weekend_window()
    days = []
    cur = start
    while cur <= end:
        wd = cur.weekday()
        if wd == 4: dl = "sex"
        elif wd == 5: dl = "sáb"
        else: dl = "dom"
        days.append((dl, cur.isoformat()))
        cur += timedelta(days=1)
        if len(days) >= 3:
            break

    # Pre-score
    for p in beaches:
        p["_surf"] = surf_score(p)
        p["_swim"] = swim_score(p)
        p["_family"] = family_score(p)

    picks_html = render_picks(beaches)
    cards_html = "\n".join(render_beach_card(p, days) for p in beaches)

    related_html = " ".join(
        f'<a href="../{r}/fim-de-semana.html">{CITY_BY_SLUG[r][1]}</a>'
        for r in related if r in CITY_BY_SLUG
    )

    page_title = f"{city_name} fim de semana — praias, mar, balneabilidade | praia smart"
    canonical = f"{SITE_URL}/{slug}/fim-de-semana.html"
    page_desc = (
        f"Como vão estar as praias de {city_name} neste fim de semana de {label}. "
        f"Mar, vento, água, câmeras ao vivo, balneabilidade — atualizado a cada 15 min."
    )
    og_html = (
        f'<meta name="description" content="{page_desc}">'
        f'<meta property="og:title" content="{page_title}">'
        f'<meta property="og:description" content="{page_desc}">'
        f'<meta property="og:url" content="{canonical}">'
        f'<meta property="og:type" content="article">'
        f'<meta property="og:locale" content="pt_BR">'
        f'<meta name="twitter:card" content="summary_large_image">'
        f'<link rel="canonical" href="{canonical}">'
    )

    beach_items = [
        {
            "@type": "Beach",
            "name": p["beach"],
            "url": f"{SITE_URL}/beach/{p['id']}.html",
            "address": {"@type": "PostalAddress", "addressLocality": city_name, "addressRegion": p["state"], "addressCountry": "BR"},
        }
        for p in beaches
    ]
    ld = {
        "@context": "https://schema.org",
        "@type": "TouristDestination",
        "name": f"{city_name} — fim de semana",
        "description": page_desc,
        "url": canonical,
        "touristType": "beachgoer",
        "includesAttraction": beach_items,
        "dateModified": datetime.now().isoformat(timespec="seconds"),
    }
    ld_html = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#F4EFE4">
<title>{page_title}</title>
{og_html}
{ld_html}
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
    <h1>{city_name} neste fim de semana</h1>
    <div class="topbar-meta">{state} · fim de semana de {label}</div>
  </div>
  <span class="wordmark"><span class="wm-praia">praia</span><span class="wm-smart">smart</span></span>
</header>

<main>

  <section class="intro">
    <h2>{city_name} neste fim de semana.</h2>
    <p>Como vão estar as praias de {city_name} neste fim de semana de {label}. Mar, vento, água, câmeras ao vivo, balneabilidade — atualizado a cada 15 min.</p>
  </section>

  <div class="section-tag">o que fazer</div>
  {picks_html}

  <div class="section-tag">por praia · sábado e domingo</div>
  {cards_html}

  {AD_HTML}

  <section class="about">
    <h3>Sobre as praias de {city_name}</h3>
    <p>{blurb}</p>
  </section>

  <div class="section-tag">veja também</div>
  <div class="crosslinks">{related_html}</div>

</main>

<div class="footer">dados Open-Meteo · cam YouTube · atualizado a cada 15 min</div>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────
# Sitemap append
# ─────────────────────────────────────────────────────────────

def append_sitemap_city_urls():
    """Rewrite web/sitemap.xml to also include the 10 city pages.

    build.py runs before us and writes a sitemap with 15 URLs. We
    re-read it, append the 10 city URLs (idempotently), and overwrite.
    """
    sm_path = os.path.join(OUT_ROOT, "sitemap.xml")
    if not os.path.exists(sm_path):
        return
    raw = open(sm_path).read()
    lastmod = datetime.now().strftime("%Y-%m-%d")
    new_entries = []
    for slug, *_ in CITIES:
        loc = f"{SITE_URL}/{slug}/fim-de-semana.html"
        if loc in raw:
            continue
        new_entries.append(f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod></url>")
    if not new_entries:
        return
    raw = raw.replace("</urlset>", "\n".join(new_entries) + "\n</urlset>")
    open(sm_path, "w").write(raw)
    print(f"Appended {len(new_entries)} city URLs to sitemap.xml")


# ─────────────────────────────────────────────────────────────
# Homepage city-pill row injection
# ─────────────────────────────────────────────────────────────

CITY_PILL_MARKER_START = "<!-- city-pills:start -->"
CITY_PILL_MARKER_END = "<!-- city-pills:end -->"


def inject_homepage_pills():
    """Inject (or replace) a row of city-pill links into web/index.html.

    Placed right after the .hero section. Idempotent — uses marker comments.
    """
    idx = os.path.join(OUT_ROOT, "index.html")
    if not os.path.exists(idx):
        return
    html = open(idx).read()

    pills_inner = " ".join(
        f'<a href="{slug}/fim-de-semana.html">{name}</a>'
        for slug, name, *_ in CITIES
    )
    block = (
        f'{CITY_PILL_MARKER_START}\n'
        f'<section class="hero" style="padding-top:0">'
        f'<div class="crosslinks" style="margin:6px 0 0;font-family:var(--font-mono);'
        f'font-size:11px;color:var(--ink-soft);letter-spacing:0.04em;">'
        f'<span style="margin-right:6px;text-transform:uppercase;">fim de semana ·</span>'
        f'{pills_inner}'
        f'</div></section>\n'
        f'{CITY_PILL_MARKER_END}'
    )
    # Inline styles so we don't depend on cities.py CSS in homepage.
    block_styled = block.replace(
        '<a href="',
        '<a style="display:inline-block;padding:5px 11px;border-radius:999px;'
        'background:var(--card);border:1px solid var(--line);color:var(--ink);'
        'margin:3px 4px 3px 0;font-family:var(--font-sans);font-weight:600;'
        'font-size:12px;letter-spacing:-0.005em;text-decoration:none;" href="'
    )

    if CITY_PILL_MARKER_START in html and CITY_PILL_MARKER_END in html:
        pre, _, rest = html.partition(CITY_PILL_MARKER_START)
        _, _, post = rest.partition(CITY_PILL_MARKER_END)
        html = pre + block_styled + post
    else:
        # Insert after the first </section> closing the hero.
        anchor = '</section>'
        i = html.find(anchor)
        if i == -1:
            return
        j = i + len(anchor)
        html = html[:j] + "\n" + block_styled + html[j:]
    open(idx, "w").write(html)
    print(f"Injected city pills into {idx}")


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    postos = json.load(open(DATA))
    by_id = {p["id"]: p for p in postos}

    written = 0
    for slug, city_name, state, beach_ids, blurb, related in CITIES:
        beaches = [by_id[b] for b in beach_ids if b in by_id]
        if not beaches:
            print(f"  skip {slug}: no beaches found in conditions.json")
            continue
        outdir = os.path.join(OUT_ROOT, slug)
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, "fim-de-semana.html")
        open(path, "w").write(render_city_page(slug, city_name, state, beaches, blurb, related))
        print(f"  wrote {path} ({len(beaches)} beach{'es' if len(beaches) != 1 else ''})")
        written += 1
    print(f"Wrote {written} city pages")

    append_sitemap_city_urls()
    inject_homepage_pills()


if __name__ == "__main__":
    main()
