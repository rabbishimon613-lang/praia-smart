# Global monetization — per-market pricing & revenue arc

Strategic and brand context lives in `notes/strategy/expansion-roadmap.md` and `brand-architecture.md`. This doc is the **money side** of that plan — what we charge venues in each market and what the ARR trajectory looks like.

## Per-market featured-slot pricing

Same product (1 featured slot per posto per category, one-month rolling), priced to the local economy. All prices are **per slot, per month**, for the standard featured tier.

| Market | Brand | Price (local) | Price (USD eq) | Why this number |
|---|---|---|---|---|
| Brasil | praia smart | R$500 | ~$100 | What R$/mo a small kiosk can absorb; covers cost in 1 extra weekend party |
| Portugal | praia smart | €120 | ~$130 | EU rates; Lisboa/Algarve venues have higher tickets |
| Cape Verde | praia smart | €80 | ~$85 | Smaller economy, tourism-heavy but local-currency sensitive |
| Argentina | playa smart | ARS$80.000 | ~$80 | Inflation-indexed quarterly; USD-equivalent target |
| Uruguay | playa smart | UYU$4.500 | ~$110 | Punta del Este premium; coastal economy strong |
| Chile | playa smart | CLP$95.000 | ~$100 | similar to BR profile |
| España | playa smart | €180 | ~$195 | Costa del Sol / Balearics premium tourism |
| México | playa smart | MX$1.800 | ~$95 | Riviera Maya peso prices |
| Italia | spiaggia smart | €200 | ~$215 | *stabilimenti* season-pass economy; high ticket |
| France | plage smart | €220 | ~$240 | Côte d'Azur premium |
| Grecia | paralía | €150 | ~$160 | Islands tourism, USD-pegged tickets |
| Malta | bajja | €180 | ~$195 | Beach-club cocktails at €15+ justify it |

**Blended global average target: ~$150/mo per slot** by 2028.

## Tier structure carries across markets

Same five tiers as Brazil playbook (see `revenue-model.md`):
1. Free directory — €0 / R$0
2. Verified (owner-claimed) — €0 / R$0
3. **Featured** — see table above
4. Event spotlight — 10-20% of monthly featured price per event
5. Multi-beach chain pack — 4-10× featured price, depending on size

## Per-market sales motion differences

Not every market sells the same way. Notes per region:

### Brasil (2026)
- **Channel:** Renata (secretary) outbound email + WhatsApp follow-up + Shimon (CEO) video call closes
- **Trust signal:** "NYC-based" framing helps
- **Payment:** Pix (instant, free, owner already uses daily)
- **Sales cycle:** 5-15 days from cold email to first payment

### Portugal + Cape Verde (2027 H1)
- **Channel:** Same playbook works (PT-PT formality slightly different; adjust email tone)
- **Trust signal:** "Brand opera no Brasil há X anos" — Brazil legitimacy helps PT
- **Payment:** SEPA bank transfer + MB Way
- **Sales cycle:** longer (PT business culture is slower, expect 2-4 weeks)

### Argentina + Uruguay (2027 H2)
- **Channel:** Need a local rep ("Renata-AR") in Buenos Aires for trust. Cold US-call doesn't land.
- **Trust signal:** Brazilian success story translates well (geographic proximity)
- **Payment:** **Critical** — Argentine inflation makes USD billing essential. Use Stripe Atlas + USDC settlement if possible. Avoid pesos in our books.
- **Sales cycle:** 7-14 days, but renewal management is a hassle (peso volatility)

### Mediterranean (2028)
- **Channel:** Per-country sales lead. Italian beach-club managers don't take English-only pitches well; Italian native required. Same for French Riviera.
- **Trust signal:** EU brand legitimacy + appearance on Italian/French press
- **Payment:** SEPA, Stripe EU
- **Sales cycle:** 14-30 days (Mediterranean business culture)

### Malta (2028 — separate from above)
- **Channel:** English direct works. Country is small enough for one part-time rep to cover.
- **Trust signal:** Malta business circles are tight; one early reference customer unlocks dozens
- **Sales cycle:** 5-14 days

## ARR projection (revised, multi-market)

| Year-end | Markets live | Paying venues | Avg $/venue/mo | Monthly recurring | ARR |
|---|---|---|---|---|---|
| 2026 | BR | 50 | $100 | $5k | $60k |
| 2027 | BR + PT + CV + AR + UY | 200 | $110 | $22k | $264k |
| 2028 | + IT + FR + ES + MT + GR | 600 | $130 | $78k | $940k |
| 2029 | + tourism arbitrage | 1200 | $135 | $162k | $1.95M |
| 2030 | + mature markets | 2500+ | $140 | $350k+ | **$4.2M+** |

By 2028 we cross **$1M ARR** purely on featured slots. Adjacent revenue streams below add on top.

## Adjacent revenue streams (cross-market)

These layer on once each market has a venue base:

### Event spotlights (every market)
- Beach festivals, surf comps, summer concerts, beach-club residencies
- 10-20% of monthly featured price per event
- High-margin, high-conversion (urgency)
- Estimated 20-30% revenue contribution by 2029

### Tourism board licensing (Mediterranean + Caribbean)
- Setur RJ / Greek tourism / Maltese MTA / etc. pay us for visitor-flow data
- Enterprise tier: $5k-50k/year per board
- Long sales cycle (12+ months) but very sticky once signed
- Estimated 5-10 board deals by 2030

### Branded content / sponsored hero cards
- Cervejas BR (Heineken, Brahma, Itaipava), Aperol (IT/FR), Estrella Damm (ES)
- Sunscreen brands (Nivea, La Roche-Posay, Sundown)
- Each market's "best for sol" hero card has sponsorship potential
- $2k-20k/month per market per brand
- Estimated 10-15 brand deals across markets by 2030

### Premium API
- Hotel chains: occupancy correlation with beach conditions
- Surf schools: lesson scheduling based on forecast
- Real-estate: "beach quality index" for coastal listings
- B2B SaaS pricing: $500-5k/month per customer
- Estimated 30-50 API customers by 2030

### Affiliate partnerships
- Booking.com hotel near beach (3-5% commission)
- GetYourGuide tours (10-15% commission)
- Uber/99 deep-link kickbacks (if negotiable)
- Lower-margin but zero sales work
- Estimated 10-15% revenue contribution

## Realistic full-revenue projection (all streams, by 2030)

| Stream | 2030 ARR estimate |
|---|---|
| Featured slots | $4.2M |
| Event spotlights | $1.5M |
| Tourism board licensing | $300k |
| Branded content | $1.2M |
| Premium API | $800k |
| Affiliates | $500k |
| **Total** | **$8.5M ARR** |

That's the realistic upper-bound vision-narrative for an investor deck circa 2027 ("we project $8M ARR by 2030 across 8 markets with these 6 revenue streams").

## Defensive moats per market

Why a new entrant can't just copy us in market X:

- **Data integration** — 8+ regional sources per market, each with quirks. 3+ months to replicate per market.
- **Venue relationships** — claimed listings = embedded CRM. Switching cost is real once a venue has 6 months of "praia smart drives 30% of my Saturday covers."
- **Brand authority** — by year 2 in each market, "praia smart" / "playa smart" is a recognized name in coastal-business circles. Hard to dislodge.
- **SEO compounding** — Google rankings only get stronger with age + content velocity
- **Cross-market knowledge transfer** — what we learn in BR helps PT/AR launches; what we learn in MT helps GR launches. Single-market competitors can't compound this way.

## What this means for 2026 priorities

Three things to nail in BR this year so the multi-market arc holds:

1. **Get to 50 paying venues** — proves featured-slot tier is real
2. **Document the playbook end-to-end** — outreach scripts, call cadence, contract template, retention numbers. So 2027 expansion isn't "Renata reinvents how we sell"; it's "Renata-PT/AR/IT runs the script."
3. **i18n the codebase** — single biggest tech blocker for 2027 launches. Should land in Q3 2026 so a new market is a 2-week project, not a 2-month rebuild.

If those three are in place by EOY 2026, the rest of this doc executes. If they're not, the global vision is just a slideshow.
