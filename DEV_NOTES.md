# praia smart — dev notes

Living doc for decisions, ideas parked for later, and gotchas. Not user docs.

## Deploy / infrastructure (current as of 2026-05-19)

- **Domain:** `praiasmart.com` (NOT .com.br — gets the bug-prone .com.br wrong; canonical, og:url, sitemap, Plausible all must use bare `.com`)
- **DNS / CDN:** Cloudflare
- **Origin:** GitHub repo `rabbishimon613-lang/praia-smart`, branch `main` — site is served from the latest committed `web/*` files
- **Refresh cadence:** every 15 min via `.github/workflows/refresh.yml` (cron). Workers fetch → `build.py` → `detail.py` → `cities.py` → commit + push
- **SSL:** Cloudflare-managed (auto)
- **Workers/scrapers:** run inside the same GitHub Actions job — no separate VPS yet
- **Analytics:** Plausible script in `<head>`, domain `praiasmart.com` (need to actually sign up at plausible.io to receive data)
- **Search Console:** not yet verified — pending the user pasting the verification meta tag in chat

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

## Shelved — pre-launch checklist (winter 2026, resume before Dec busy season)

Status snapshot as of 2026-05-19. App is live at praiasmart.com via Cloudflare,
served from rabbishimon613-lang/praia-smart GH repo, refreshing every 15 min.

### User-action items (waiting on Pedro, not Claude)

- **Google Search Console verification** — go to search.google.com/search-console,
  add property `https://praiasmart.com` (URL prefix, not Domain), pick HTML tag
  verification, paste the `<meta name="google-site-verification" content="...">`
  string to Claude. Claude will inject it in `build.py` <head>, push, wait one
  15-min cron tick, then click "Verify". After verify → submit sitemap at
  `https://praiasmart.com/sitemap.xml`. Same drill for Bing Webmaster Tools
  (gives Yahoo + DuckDuckGo for free).
- **Plausible account** — script is live in <head> with `data-domain="praiasmart.com"`
  but no account exists yet at plausible.io. Sign up (~$9/mo) OR swap script to
  Umami self-host / GoatCounter free / etc. Until signed up, no data is collected.
- **First backlink push** — draft post ready (r/rio recommended). Copy-pasteable
  draft was in the chat on 2026-05-19. Find it via:
  `git log --all --oneline | grep -i seo` then look in conversation history.
  Key points: title "Fiz um site que mostra condições das praias do Rio em
  tempo real — câmera ao vivo + balneabilidade do INEA". Post as personal
  weekend-project, not corporate. Don't go to r/brasil first.
- **Domain fact-checks for beach descriptions** — agent flagged these to verify
  in `web/beach_descriptions.py`:
  - Balneário Rincão emancipation year (2013)
  - Santos Gonzaga Guinness "longest beachfront garden" claim
  - Praia Grande "Eye" Ferris wheel still operating
  - Copa Posto 5 phrasing — does it read right to a carioca?

### Open eng work (when we resume)

- **News filter cleanup** — substring matching "barra" hits unrelated stories.
  Real fix: small LLM classifier (per existing DEV_NOTES item). Looks
  unprofessional on launch; do before any marketing push.
- **Lighthouse / perf audit** — never run. Catch render-blocking, image
  sizing, CLS issues before summer traffic. Mobile-first.
- **Phone QA pass** — open homepage + 12 detail pages + 10 city pages on a
  real iPhone + a real cheap Android. Look for broken layouts, slow loads,
  weird empty states.
- **Cameras for 11 new top-20 beaches** — water data is wired for Ipanema,
  Barra, Boa Viagem, Pajuçara, Iracema, Jurerê, Porto de Galinhas, Itapuã,
  Geribá, Tramandaí, Porto Seguro (and sits unused in balneabilidade.json
  for several). To surface them, need YouTube cam IDs + postos.csv rows.
  Cam-first rule means they won't render without cams.
- **INEMA bahia worker quirk** — scrapes the news article (not PDF) because
  `homologa.ba.gov.br` is geo-blocked outside Bahia. Works but fragile. No
  E.coli numbers since article is prose. Consider VPS-in-BA fix later.
- **IMA-SC date routing** — currently misses the off-season monthly bulletin.
  In-season (Oct-Mar) it should work. Floripa/Camboriú/Rincão + Jurerê
  Internacional all show sem_dados during winter. Verify when October hits.
- **FEPAM seasonal** — Tramandaí/Capão da Canoa only get data Dec-Feb
  ("Operação Verão Total"). Worker correctly stubs sem_dados off-season.
  No fix needed; just be aware of the user-facing "fora de temporada" message.
- **API sniffs that failed** — Vai dar Praia (BA INEMA app) and Semace Digital
  (CE) both probed; no public JSON endpoints found. If those apps ever
  publish API docs or someone reverse-engineers them, refactor the workers
  to use JSON instead of HTML/PDF scraping.

### Bonus integrations parked (P3.3, P3.4, P3.5 stubs exist)

- **Orla Rio bandeiras** — `workers/orla_rio.py` is a stub. Real path to
  unlock this: CV (YOLOv8 + color sampling) on Orla Rio live cam frames
  (Surfview iframes embed lifeguard posts). Same pipeline as the planned
  crowd-counting CV. Build them together — same architecture.
- **Observatório do Turismo calibration** — `workers/turismo_calibration.py`
  is a stub. Real path: add a PDF/XLSX parser per state observatório
  (BA, CE, SP, RJ, PE, AL all identified). Multiply agito.py base-rates by
  `monthly_visitors / baseline`. Doesn't unlock beaches, makes existing
  crowd predictions calibrated to real foot-traffic.
- **LAPIS/UFAL satellite supplement (NE coast)** — `workers/lapis_satellite.py`
  is a stub. LAPIS hosts unresolvable at last check; EUMETSAT View has the
  data but is JS-only. Real path: pick a free EUMETSAT WMS layer ID
  (`msg_iodc_natural` is a candidate), mirror it via `satellite.py`'s
  `fetch_crop()` pattern, surface as cloud-fallback panel for NE beaches
  (Boa Viagem, Pajuçara, Porto de Galinhas, Salvador).

### What's already shipped this winter sprint (don't re-do)

- INEA XLSX parser (was image-PDF, now openpyxl-based — 7 Rio beaches live)
- CETESB SP, INEMA BA, CPRH PE, SEMACE CE, IMA-AL workers — all live
- Dynamic top-4-of-10 dial system (publico/ar/uv/ondas/vento/calor/mar_quente/ceu/mare)
- Dedicated água box (status + age + rain overlay)
- Light "praia 10am" UI redesign across homepage + detail + sub-pages
- Sun arc score viz, hourly strips, crowd meter parasols, sunset hero
- SEO: per-page titles with "hoje" keyword, meta description, OG, Twitter
  card, canonical, sitemap.xml, robots.txt
- schema.org JSON-LD (BeachWeather per detail, WebSite + SearchAction home)
- Plausible analytics script (waiting on account signup)
- 12 hand-written ~150-word PT-BR beach descriptions
- 10 auto-generated city "fim de semana" pages with cross-linking
- Ads via A-Ads unit 2438146 (homepage card injection + 2 per detail page)
- FEPAM RS worker (season-aware, off-season stub)
- SEO sprint #2: FAQ schema (`FAQPage`), BreadcrumbList, VideoObject JSON-LD,
  "praias próximas" haversine internal linking, 12 `/{city}/webcam-ao-vivo.html`
  landing pages, lazy-loaded iframes, preconnect hints, favicon (coral half-sun
  SVG), footer with data-source citations. Sitemap now 37 URLs.
- News filter keyword fix (word-boundaries + negative blocklist) — note: news
  ticker is NOT currently rendered in the UI, so this is prep, not live
- Domain live at praiasmart.com via Cloudflare; canonical/og/analytics all
  corrected from the wrong .com.br to .com

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
