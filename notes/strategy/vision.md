# Vision

## The one-liner

**We are the decision layer for going to the beach — global, but localized everywhere.**

Each market gets its own native-language brand (praia smart in BR/PT, playa smart in ES-speaking markets, spiaggia smart in Italy, plage smart in France, etc.) — one shared platform underneath. See `brand-architecture.md` and `expansion-roadmap.md` for details.

We start with **praia smart at praiasmart.com — the Brazilian property**. Prove the model here in 2026, then roll out to PT-Atlantic + Argentina in 2027, Mediterranean in 2028.

It's the app you open the morning of — sometimes the night before — when you're choosing where to go, when to leave, and what to do once you're there. Same job in every language.

## The verb test

Long-term success looks like *each regional brand becoming a verb in its market*:

> *"Olha no praia smart antes de ir."* (BR — carioca)
> *"Mirá en playa smart antes de ir."* (Argentina — rioplatense)
> *"Guarda lo spiaggia smart prima di andare."* (Italia)
> *"Regarde plage smart avant d'y aller."* (France)
> *"Check bajja before you go."* (Malta — english)

When the BR sentence sounds natural to a carioca, paulistano, baiano, or potiguar — we've won the Brazilian category. Same way *"olha no Google Maps"* replaced "look it up on a map." We want *"praia smart"* to replace whatever fragmented thing people do today (open Climatempo, then INEA PDF, then YouTube live cam, then Instagram).

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

## Multi-year arc (summary — full detail in `expansion-roadmap.md`)

- **2026 — Brazil only.** Prove the model. 50 paying venues, R$25k/mo recurring.
- **2027 H1 — Portugal + Cape Verde.** Same language, EU mandated open water-quality data, easy. Same brand: praia smart on .pt / .cv.
- **2027 H2 — Argentina + Uruguay.** *Inverted seasons* — keeps team busy during BR winter. New brand: **playa smart**.
- **2028 — Mediterranean (Italy + France + Spain + Malta + Greece).** Four new sister brands launching together: **spiaggia smart**, **plage smart**, **playa smart** (ES), **bajja** (Malta), **paralía** (Greece). EU data advantage makes this faster than expanding within Brazil.
- **2029 — Tourism arbitrage markets** (Caribbean, Mexico tourist corridor, Bali, Phuket — English wrapper).
- **2030+ — Mature markets with funding** (US, Australia, UK).

Brazil dominance comes first. Without that, expansion is just thrash. But the *vision* is global from day one — every architecture decision should support eight languages eventually, even if today only one is live.

## The bigger philosophical thing

Beaches are public goods. The data about them (water quality, conditions, crowd) is public good adjacent — collected by state agencies on taxpayer money. The current state is **the data exists but is unusable**.

praia smart's job is **making public-good data feel like a private-product experience.** Same impulse as Stripe wrapping bank rails, or Google Maps wrapping GIS data. The data wasn't ours; the UI is. That's the value capture.

If that's the frame, the long-term win isn't just monetization — it's becoming **infrastructure for the Brazilian beach economy.** Tourism boards eventually pay us to know where visitors are going. Hotels pay us for room-fill optimization. Brewery brands pay for "best beach for Heineken's weekend activation."

The current pitch (R$500/mo to a kiosk owner) is the seed. The flywheel is data ↔ users ↔ venues ↔ data.

That's the real vision.
