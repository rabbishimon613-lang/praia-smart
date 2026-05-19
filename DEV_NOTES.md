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

## Auto-generated video — TikTok bot (queued for summer 2026-27, Dec onward)

Reference: @damnlines.com — automated trading/finance TikTok, daily cadence,
no face cam, just chart + TTS overlay. Praia smart equivalent: daily auto-video
per beach, queued for busy season (Dec-Feb when traffic peaks).

### Format (decided)
- **Vertical 1080×1920**, 25–40s
- Background: live cam still (or short looped clip if youtube-dl can grab one)
- Foreground: score dial overlay + "ao vivo" badge + watermark + beach name + posto
- TTS narration (PT-BR carioca): "Copacabana Posto 5 agora — mar bom, UV 6,
  água própria pela INEA. Melhor surfar: 7 às 10. Melhor banho: até 11."
- Audio bed: ambient wave loop from CC source (freesound.org)
- End-card: praiasmart.com.br + "link na bio"

### Distribution
- **TikTok** primary (@praiasmart) — 1 video per top-traffic beach per day
- IG Reels mirror via cross-post (no extra render)
- YouTube Shorts mirror (no extra render)
- NOT to Twitter (no traction expected for beach content)

### Cadence
- Top 5 beaches daily (Copa, Ipanema, Barra, Pajuçara, Iracema)
- Other beaches: 1x/week, picking the highest-score moment
- Special: "água imprópria" alert videos when balneabilidade flips red — urgent format, different visual treatment

### Tech stack (when we build)
- ffmpeg for assembly (image + audio + text overlays)
- TTS: Edge TTS BR (free) for v1; ElevenLabs PT-BR voice if budget allows
- TikTok upload: no official API for orgs without partnership — likely
  semi-manual (render to file, batch upload via mobile) OR use a service
  like Hootsuite/Buffer that handles TikTok scheduling
- Render in GitHub Actions, push artifact to a /videos/ folder

### Build order when summer approaches
1. Single-beach prototype renderer (one Copa video end-to-end)
2. TTS quality A/B (Edge vs ElevenLabs)
3. Template variations (good day vs imprópria-alert)
4. Auto-pick logic ("which beach today?")
5. Batch render + upload pipeline
6. Analytics loop (which videos drive traffic)

### Idea: rendered video with UI snapshot
(Original parked notes preserved below)
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
