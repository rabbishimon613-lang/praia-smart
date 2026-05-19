# praia smart — UI Overhaul Handoff

**For:** Claude Design
**From:** product owner
**Date:** 2026-05-18
**Goal:** Replace the current dark-mode UI with a **light, informative, beach-themed** redesign that feels innovative but stays dead-simple to use.

---

## 1. What the app is, in one breath

**praia smart** is a real-time, cam-first dashboard for Brazilian beaches. For each beach, it tells you — right now — whether it's good for **surfing, swimming, sunbathing, or avoiding the sun**, plus shows a live YouTube cam and the predicted best 3-hour window of the day per activity.

Think: *"AccuWeather, but only for beaches, and it actually tells you what to do."*

Currently live (Rio + a handful of Santa Catarina / Cabo Frio spots). Multi-region — header still says "Rio" but that's a known stale copy item.

## 2. Who it's for

- **Primary:** Brazilians in coastal cities deciding *which beach to go to today*, or *when in the day to go*. Mobile-first, often opened on the bus / between meetings.
- **Secondary:** Surfers checking conditions across spots; tourists who don't know which posto is which.
- Locale: **pt-BR**. All copy is Portuguese. Designs must accommodate Portuguese word lengths (often longer than English).

## 3. The vision

A redesign that feels like **standing on the sand at 10am** — bright, breezy, optimistic, sun-on-skin. Not a weather app. Not a corporate dashboard. The current dark navy/teal UI (see `web/index.html`) is functional but feels like a Bloomberg terminal. We want the opposite.

**Three words:** *light, informative, beach.*

**Mood references to evoke (not copy):**
- Sun-bleached pastels — sand, sea foam, sky blue, coral, terracotta tile
- Brazilian modernism — Niemeyer curves, Burle Marx wavy mosaics (Copacabana sidewalk!)
- Light, airy, generous whitespace — like an open beachfront window
- Soft shadows, no hard borders, rounded everything
- A whisper of texture (grainy sand, watercolor wash) — but never noisy

**Anti-references — do NOT do:**
- Dark mode / "pro trader" aesthetic (← what we have now)
- Skeuomorphic sand/water (no literal beach photo backgrounds)
- Surf-brand neon (Quiksilver / Rip Curl tropes)
- Generic SaaS — gradients-and-glass, Stripe-clone, etc.

## 4. Hard constraints

- **Mobile-first.** ~80% of traffic is phone. Desktop is a nice-to-have grid.
- **Information density matters.** Each beach card carries: name, posto number, live cam thumb, surf/swim/sun scores, badges, best-window text, crowd estimate. Don't sacrifice scannability for whitespace. Light ≠ empty.
- **Static HTML output.** The site is built by `web/build.py` from JSON. No React, no SPA framework. Final deliverable should be CSS + minimal vanilla JS, droppable into the existing Jinja-less template strings in `build.py`. (If you want to propose a build-tool change, flag it — don't assume it.)
- **Performance budget:** must load fast on 4G in Brazil. No huge hero images, no webfonts heavier than ~40kb total. System font stack is currently fine.
- **Ads.** A-Ads iframe slots are injected after cards 2, 7, 12, 17, 22. Design must accommodate a 90px-tall banner ad mid-stream without breaking rhythm.
- **Accessibility:** WCAG AA contrast on a light palette is harder than it looks — please verify. Sun glare is a real use case; high-contrast mode toggle would be a bonus.

## 5. Information architecture (don't redesign this, just restyle)

**Top of page** — sticky header
- Logo / wordmark ("praia smart")
- Subtitle (current condition summary)
- Pill filter row: "todas / surfar / nadar / sol / evitar sol" + nav pills ("melhores", "sobre")

**Hero strip** — 3 cards above the fold
- "melhor pra surfar agora" / "melhor pra nadar" / "melhor pra sol"
- Each names a beach + one-line why

**Main feed** — beach cards, sorted by surf score
- Card header: beach name, posto number, badges (surf/swim/warm-water/etc.)
- Live cam embed (YouTube iframe, 16:9)
- Activity scores (4 of them: surfar, nadar, sol, evitar sol) — currently numeric 0-1, could become visual
- Best-window strip ("melhor surfar: 7-10h")
- Conditions row: wave height, period, wind, UV, water temp, air temp, cloud %
- Crowd bucket (vazia / moderada / cheia / lotada)
- Optional: news ticker, alerts banner

**Detail pages** — `web/beach/<slug>.html`, per beach. Same data, expanded.

**Other pages:** `melhores.html` (rankings), `sobre.html` (about).

## 6. Brand-ish bits we'd love you to figure out

- A **wordmark** for "praia smart" — currently just bold text. Should feel handmade-ish, not corporate.
- An **icon set** for the four activities (surf, swim, sun, shade) that isn't emoji. Current build uses 🏄 ☀️ 🌊 etc. — emoji are inconsistent across platforms and look childish.
- A **score visualization** primitive — replace the raw 0.000–1.000 numbers with something glanceable (dots? a wave? a sun arc?). This is the single highest-leverage piece of the redesign.
- A **crowd indicator** — currently a text bucket. Could be a tiny stylized parasol-count or similar.

## 7. What's coming (so the design doesn't paint us into a corner)

From `DEV_NOTES.md` — features queued post-redesign:

- **Social feed layer (v1.5)** — Bluesky / YouTube Shorts / user submissions per beach. Will need a bottom-sheet pattern per card + a city-wide "ao vivo" tab. Please design with this slot reserved.
- **User-submitted photos** — geotagged uploads. Need a thumbnail-grid pattern and a clear "submit" affordance.
- **Crowd CV (computer vision)** — automated crowd-count from cam frames, will replace the manual bucket. Numbers will get more precise; design for "247 people on the sand" not just "moderada".
- **Auto-generated short videos** — daily TTS-narrated condition recaps. Will need a video-player card or feature row.
- **Multi-region** — currently Rio-heavy, expanding to Floripa, Cabo Frio, Camboriú, Natal. Header copy + nav must generalize. Probably needs a region switcher.
- **Sunset card** — at night the "sol" hero card should swap to a sunset / "amanhã" mode.

## 8. Files to read for ground truth

```
/Volumes/EOS_DIGITAL/praia/
├── DEV_NOTES.md          ← roadmap + decided/parked items
├── web/
│   ├── index.html        ← current homepage (519 lines, all inline CSS) — your "before"
│   ├── build.py          ← generates index.html from JSON; redesign lands here
│   ├── beach/*.html      ← per-beach detail pages
│   ├── melhores.html
│   └── sobre.html
└── data/                 ← conditions.json, alerts.json, news.json, agito.json
```

Look at `web/index.html` first — the current CSS variables block at the top is the cleanest summary of the existing system. Replace it with the new one.

## 9. Deliverables we want back

1. **Visual concept** — 2–3 mockups (mobile + desktop): home hero, one beach card expanded, one detail page.
2. **Design tokens** — colors, type scale, spacing, radii, shadows, motion. As CSS custom properties, drop-in for `index.html`.
3. **Component spec** — beach card, hero card, pill, badge, score viz, crowd indicator, ad slot.
4. **A short rationale** — why these palette/type choices serve "light, informative, beach". Not a deck, just a paragraph per major decision.
5. **An implementation note** — what `build.py` and the HTML templates need to change. Concrete, file-and-function level.

Out of scope for v1: full design system docs, Figma library, illustration set. We can iterate.

## 10. Open questions to answer in your proposal

- Light mode only, or light + auto-dark for night beach-checking?
- Serif accent for the wordmark, or all sans?
- How much motion? (subtle wave shimmer on hero? or fully static?)
- Do we have a mascot? (probably not, but tell us if you think we should.)

---

That's the package. Lean into "Brazilian beach at 10am". Make it the app people screenshot.
