"""Hourly activity scoring + best-window finder.

For each beach's 24h hourly forecast, compute scores for:
  - surfar      : wave sweet-spot × period × offshore wind × daylight
  - pegar_sol   : UV in safe range × low cloud × low wind × daylight
  - evitar_sol  : low UV × daytime (sunny but won't burn — early/late hours)
  - movimento   : weather-prior (hour-of-day × weekend × warmth × clarity)

Then slide a 3-hour window to find the peak window per activity.
"""
import math
from datetime import datetime


def _bell(x, center, width):
    return math.exp(-((x - center) ** 2) / (2 * width ** 2))


def _offshore_component(wind_dir):
    """South-facing beaches: wind from north (0°) = offshore (positive)."""
    if wind_dir is None:
        return 0.0
    return math.cos(math.radians(wind_dir))


def score_surf(h):
    wave = h.get("wave") or 0
    period = h.get("period") or 0
    wind = h.get("wind") or 0
    wind_dir = h.get("wind_dir")
    uv = h.get("uv") or 0
    # Sweet spot 1.5m, zero outside 0.4-3.0m
    size = _bell(wave, 1.5, 0.9) if 0.4 <= wave <= 3.0 else 0
    period_s = min(period / 14, 1.0)
    offshore = max(0, _offshore_component(wind_dir)) * min(wind / 12, 1.0)
    daylight = 1.0 if uv > 0 else 0.2
    return round(daylight * (size * 0.5 + period_s * 0.3 + offshore * 0.2), 3)


def score_sun_bathe(h):
    uv = h.get("uv") or 0
    cloud = h.get("cloud") or 0
    wind = h.get("wind") or 0
    if uv <= 0:
        return 0
    # UV sweet spot 3-7: enough to tan, not dangerous
    if uv < 3: uv_s = uv / 3 * 0.6           # ramps up
    elif uv <= 7: uv_s = 1.0                  # peak
    else: uv_s = max(0, 1 - (uv - 7) / 4)    # ramps down (too dangerous)
    clear = (100 - cloud) / 100
    breeze = max(0, 1 - wind / 25)
    return round(uv_s * 0.5 + clear * 0.3 + breeze * 0.2, 3)


def score_sun_avoid(h):
    """For sun-sensitive folks: bright enough to be outside, but UV is mild."""
    uv = h.get("uv") or 0
    cloud = h.get("cloud") or 0
    # Daytime but UV low (early morning, late afternoon, or cloudy)
    if uv <= 0:
        return 0  # night — irrelevant
    if uv > 6:
        return 0  # too dangerous, skip
    safe_uv = 1 - uv / 6        # lower UV = higher score
    cloud_bonus = cloud / 100 * 0.3  # cloudy days are good too
    return round(safe_uv * 0.7 + cloud_bonus, 3)


def score_movimento(h, is_weekend):
    """Heuristic prior — no CV yet. Peak hours × weekend × warmth × clarity."""
    hour = h["hour"]
    cloud = h.get("cloud") or 0
    temp = h.get("temp") or 0
    uv = h.get("uv") or 0
    if uv <= 0:
        return 0  # night — nobody on beach
    # Bell curve centered at 13.5h, σ=2.5
    time_f = _bell(hour, 13.5, 2.5)
    weekend_f = 1.3 if is_weekend else 1.0
    # Warmth: 18°→0, 30°→1
    warmth = max(0, min((temp - 18) / 12, 1.0))
    clarity = (100 - cloud) / 100
    return round(min(1.0, time_f * weekend_f * warmth * 0.6 + clarity * 0.4), 3)


def _hour_rows(hourly):
    """Convert hourly arrays → list of dicts indexed by position."""
    if not hourly or not hourly.get("time"):
        return []
    rows = []
    for i, t in enumerate(hourly["time"]):
        try:
            hour = int(t[11:13])
        except Exception:
            hour = 0
        rows.append({
            "i": i, "time": t, "hour": hour,
            "wave": hourly["wave_m"][i] if i < len(hourly["wave_m"]) else None,
            "period": hourly["wave_period_s"][i] if i < len(hourly["wave_period_s"]) else None,
            "tide": hourly["tide_m"][i] if i < len(hourly["tide_m"]) else None,
            "temp": hourly["temp_c"][i] if i < len(hourly["temp_c"]) else None,
            "wind": hourly["wind_kmh"][i] if i < len(hourly["wind_kmh"]) else None,
            "wind_dir": hourly["wind_dir"][i] if i < len(hourly["wind_dir"]) else None,
            "uv": hourly["uv"][i] if i < len(hourly["uv"]) else None,
            "cloud": hourly["cloud_pct"][i] if i < len(hourly["cloud_pct"]) else None,
        })
    return rows


def _best_window(scores, window_h=3):
    """Slide a window of width N and return the highest-mean window."""
    if len(scores) < window_h:
        return None
    best_i, best_mean = 0, -1
    for i in range(len(scores) - window_h + 1):
        m = sum(scores[i:i + window_h]) / window_h
        if m > best_mean:
            best_mean, best_i = m, i
    return {"start_i": best_i, "end_i": best_i + window_h - 1, "score": round(best_mean, 3)}


def predict(hourly, ref_time_iso=None):
    """Return predictions for all activities. ref_time decides weekend flag."""
    rows = _hour_rows(hourly)
    if not rows:
        return None

    ref = datetime.fromisoformat(ref_time_iso) if ref_time_iso else datetime.now()
    is_weekend = ref.weekday() >= 5

    activities = {
        "surfar":     [score_surf(h) for h in rows],
        "pegar_sol":  [score_sun_bathe(h) for h in rows],
        "evitar_sol": [score_sun_avoid(h) for h in rows],
        "movimento":  [score_movimento(h, is_weekend) for h in rows],
    }

    result = {}
    for name, scores in activities.items():
        w = _best_window(scores, 3)
        if w and w["score"] > 0.05:  # threshold: don't show garbage windows
            result[name] = {
                "start_time": rows[w["start_i"]]["time"],
                "end_time": rows[w["end_i"]]["time"],
                "score": w["score"],
                "hourly_scores": scores,
            }
        else:
            result[name] = None
    return result
