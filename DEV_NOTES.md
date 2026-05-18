# praia smart — dev notes

Living doc for decisions, ideas parked for later, and gotchas. Not user docs.

## Social media push layer (queued for v1.5)

Live social feed integrated into each card + city-wide feed tab.

### Sources, in priority order

1. **Bluesky** — open API, free, hashtag/keyword search. Primary external feed.
2. **YouTube Shorts** — YouTube Data API, free 10k/day. Secondary, video content.
3. **In-app user submissions** — the actual moat. Tap-to-submit photo + text, geotagged to posto.
4. **Reddit** (r/riodejaneiro, r/brasil) — tertiary, niche but quality.
5. **Twitter/X** — paid $100/mo Basic tier. Only after revenue justifies it.

### Closed / not realistic

- Instagram (closed hashtag/geo search since 2018)
- TikTok (research API only, gated)
- Threads (gated)
- Facebook (only Page partnerships work)

### Workflow shape

```
workers/social_external.py (every 5 min)
  ├── Bluesky search by hashtag + beach context
  ├── YouTube Shorts search
  ├── Reddit JSON polling
  ↓
  normalize → {source, author, text, image, ts, beach_tags}
  ↓
  moderation (toxicity + spam keyword block)
  ↓
  dedupe → data/social.json

workers/social_submit.py (webhook)
  └── POST /submit → photo + text + lat/lng
      → NSFW classifier (NudeNet local, free)
      → toxicity filter
      → append to data/social.json

web/build.py reads social.json
  ├── per-card bottom-sheet pill "📱 N posts" → modal
  └── city-wide "ao vivo" tab next to hero strip
```

### UI options chosen

- **Bottom sheet per posto** (native mobile pattern, big content area without cramping card)
- **City-wide tab at top** for chronological mixed feed

### Moderation must-haves from day 1

- PT-BR toxicity/slur blocklist
- NSFW image classifier on uploads (NudeNet runs locally, free)
- Manual review queue (simple HTML panel)
- Brazilian-normal threshold: sunga/bikini OK, nudity not

### Build order when we get there

1. Bluesky poller → social.json schema
2. Bottom-sheet UI for one posto
3. YouTube Shorts source
4. User-submit endpoint (anon, IP rate-limited)
5. Moderation pipeline
6. Reddit source
7. City-wide tab

## Auto-generated video (queued, undefined)

Idea: rendered video with UI snapshot + (maybe) livestream screenshot + Brazilian TTS narrating conditions. User hadn't decided yet:
- Length?
- Distribution channel? (IG Reels / TikTok / in-app / Twitter)
- Per-beach or aggregate daily?
- Include live cam still or just UI?

TTS candidates to evaluate later: Coqui (open, free), Eleven Labs (paid, best quality), Google TTS BR voices, Edge TTS BR (free).

## Cam discovery

- YouTube channel pages are JS-rendered, can't enumerate via simple HTTP fetch.
- For batch discovery of channels like @LiveRioBR, need YouTube Data API (free, 10k/day quota, requires API key).
- For one-off video metadata: `https://www.youtube.com/oembed?url=...&format=json` works keyless, returns title + author. Use this to identify any URL the user drops.
- Channels to enumerate when YouTube API is wired: @LiveRioBR, @maaxcamaovivo, @Vejaomar, @Surfistafotografo, @PointdoForte, @BNU.tv, @Olhar013, @BarradaLagoaOnline, @LiveCamNatal, @MarceloPraiaGrande, EarthCam.

## Other parked items

- **INEA balneabilidade** — original URL 404s, they reorganized portal. Needs URL hunting.
- **News filter** — currently noisy (substring matches like "barra" hitting unrelated stories). Real fix: small LLM classifier later.
- **Crowd CV for P5** — full plan agreed (YOLOv8s + ROI mask + buckets, browser-based calibrator). Deserves dedicated session.
- **Sun hero card at night** — currently shows "melhor pra sol" with UV 0 after sunset. Could swap to "🌅 pôr do sol" or "melhor pra sol amanhã".
- **Header copy** — still says "Rio" but project is now multi-region. Generalize when we add more cams.

## Decided, not changing

- **Cam-first**: only beaches with a working cam show up. No placeholder cards.
- **YouTube iframe embed** for live cam display (legal, free, no infra).
- **Frame extraction via yt-dlp** only for internal CV (crowd count), never redistributed.
- **No Skyline Webcams** (ToS prohibits, paid API). Use as scouting only, find upstream.
- **No Sympla** for events (Cloudflare-walled, would need headless+stealth).
- **Open-Meteo for everything weather/marine/AQ/tide** — one host, no key, free forever.
- **Tides come from Open-Meteo `sea_level_height_msl`**, not pytides — same source.

## Stack

- Python 3 stdlib + curl (no SSL cert hell)
- SQLite eventually (currently flat JSON in data/)
- Static HTML output from build.py
- $5 VPS for workers when we deploy
