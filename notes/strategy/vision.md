# Vision

## The one-liner

**praia smart is the decision layer for going to the beach.**

It's the app you open the morning of — sometimes the night before — when you're choosing where to go, when to leave, and what to do once you're there.

## The verb test

Long-term success looks like:

> *"Olha no praia smart antes de ir."*

When that sentence sounds natural to a carioca, paulistano, baiano, or potiguar — we've won the category. Same way *"olha no Google Maps"* replaced "look it up on a map." We want *"praia smart"* to replace whatever fragmented thing people do today (open Climatempo, then INEA PDF, then YouTube live cam, then Instagram).

## North-star metric

**Sessions per active weekend day in Brazil during summer.**

Not downloads. Not signups. Not MAU. The behavior we're optimizing for: someone opens praia smart on Saturday morning to decide their day.

If we hit **100k Saturday-morning sessions** in any given summer Saturday by 2027, we've achieved escape velocity.

## Why this matters now

Brazil has ~10,000 km of coastline, ~250M people, ~3 of the top 20 most-visited beaches in the world (Copacabana, Ipanema, Ponta Negra), and **zero category-defining apps** for beach-day decisions. The state agencies publish PDFs from 2005 layouts. The weather apps are generic. YouTube live cams exist but aren't aggregated. Instagram beach accounts are vibes-only.

There's a clean, unclaimed product surface here. The infrastructure exists (Open-Meteo, state balneabilidade, YouTube cams). The data exists. Nobody put it together with a decent UI.

That's praia smart.

## What we are NOT

- **Not a weather app.** Climatempo / Tempo Agora own that. We surface weather only when relevant to beach-going.
- **Not a surf forecast.** Surfline / Windguru own that. We mention surf conditions because beach-goers care, but we don't go deep on swell modeling.
- **Not a booking engine.** Booking / Airbnb / Hurb own that. We may link to reservations, but we don't host them.
- **Not a social network.** No DMs, no profiles, no comments. The social layer (v1.5 in DEV_NOTES) is feed-style aggregation, not interaction.
- **Not a tourism guide.** No "5 places to visit in Rio." We're hyperlocal to a posto, not a city.

The discipline of saying "no" to these is how the product stays *good*. Every adjacent thing we don't build is a thing competitors can't out-feature us on, because we're tighter.

## Three-year arc

### Year 1 — Brazil (2026)

- 12 → 23 beaches (cover top-20 by attendance)
- Phase 1-3 venue monetization (free directory → claim flow → R$500/mo featured slots)
- TikTok bot during Dec-Feb busy season
- ~1k venue listings, ~50 paying
- Target: profitable on R$25k/mo by March 2027

### Year 2 — Portuguese-speaking Atlantic (2027)

- Portugal (Lisboa, Algarve, Açores) — easy data parity (EMA, IPMA, Open-Meteo)
- Brazil expansion to 50+ beaches
- Cape Verde, Madeira — language overlap, tourist destinations
- iOS + Android wrappers (PWA → native via Capacitor)
- Target: R$200k/mo on venues + light tourism-board licensing

### Year 3 — Global (2028)

- Beach destinations where decisions are made under uncertainty: Bali, Goa, Phuket, Mediterranean
- Premium API for tourism boards, hotel chains, surf schools
- Multi-language (EN, ES, FR) but PT-first DNA preserved
- Target: $5M ARR, acquisition or scale-up funding

The Brazil dominance has to come first. Without that, expansion is just thrash.

## The bigger philosophical thing

Beaches are public goods. The data about them (water quality, conditions, crowd) is public good adjacent — collected by state agencies on taxpayer money. The current state is **the data exists but is unusable**.

praia smart's job is **making public-good data feel like a private-product experience.** Same impulse as Stripe wrapping bank rails, or Google Maps wrapping GIS data. The data wasn't ours; the UI is. That's the value capture.

If that's the frame, the long-term win isn't just monetization — it's becoming **infrastructure for the Brazilian beach economy.** Tourism boards eventually pay us to know where visitors are going. Hotels pay us for room-fill optimization. Brewery brands pay for "best beach for Heineken's weekend activation."

The current pitch (R$500/mo to a kiosk owner) is the seed. The flywheel is data ↔ users ↔ venues ↔ data.

That's the real vision.
