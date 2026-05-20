# TikTok auto-video bot (queued for summer 2026/27)

Reference inspiration: **@damnlines.com** on TikTok — automated trading/finance content, daily cadence, no face cam, just chart + TTS overlay. praia smart equivalent: daily auto-video per beach, queued for busy season Dec–Feb when traffic peaks.

## Format (decided)

- **Vertical 1080×1920**, 25–40 seconds
- Background: live cam still (or short looped clip if youtube-dl can grab one)
- Foreground: score dial overlay + "ao vivo" badge + watermark + beach name + posto
- TTS narration (PT-BR carioca): *"Copacabana Posto 5 agora — mar bom, UV 6, água própria pela INEA. Melhor surfar: 7 às 10. Melhor banho: até 11."*
- Audio bed: ambient wave loop from CC source (freesound.org)
- End-card: praiasmart.com + "link na bio"

## Distribution

- **TikTok primary** (@praiasmart) — 1 video per top-traffic beach per day
- IG Reels mirror via cross-post (no extra render)
- YouTube Shorts mirror (no extra render)
- NOT to Twitter (no traction expected for beach content)

## Cadence

- Top 5 beaches daily (Copa, Ipanema, Barra, Pajuçara, Iracema)
- Other beaches: 1x/week, picking the highest-score moment
- **Special: "água imprópria" alert videos** when balneabilidade flips red — urgent format, different visual treatment, drives massive shares

## Tech stack

- **ffmpeg** for assembly (image + audio + text overlays)
- **TTS:** Edge TTS BR (free) for v1; ElevenLabs PT-BR voice if budget allows
- **TikTok upload:** no official API for orgs without partnership — likely semi-manual (render to file, batch upload via mobile) OR use Hootsuite/Buffer for TikTok scheduling
- Render in GitHub Actions, push artifact to a `/videos/` folder

## Build order when summer approaches

1. Single-beach prototype renderer (one Copa video end-to-end)
2. TTS quality A/B (Edge vs ElevenLabs — pick on cost+quality)
3. Template variations (good day vs imprópria-alert)
4. Auto-pick logic ("which beach today?" — pick highest movement+best conditions)
5. Batch render + upload pipeline
6. Analytics loop (which videos drive traffic — adjust template)

## Why this matters

- TikTok BR penetration is massive (>110M users, ~75% of internet users)
- Algorithm rewards consistent niche posters (we'd be the only beach-conditions bot)
- Each video is a free standalone SEO asset (titles + descriptions index in Google)
- Compounding flywheel: views → followers → followers see imprópria alerts → site visits → bookmarks → return traffic

## Risks

- TikTok BR has been threatening to require official partner status for automated uploads. May need to semi-manualize.
- Content fatigue: if every video looks identical, algorithm down-ranks. Need 3-4 template variations rotating.
- Voice cloning of carioca accent is imperfect with current TTS — may sound "off" to natives. Worth ElevenLabs test.

## Success metric

- Month 1: 10k followers, 5% site visit rate (500 daily visitors from TikTok alone)
- Month 3: 50k followers, 1-2 viral spikes when an imprópria alert lands during a holiday
- Month 6 (post-summer): 100k followers, sustainable referral channel for off-season SEO content
