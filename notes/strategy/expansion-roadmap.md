# Expansion roadmap

We start with **Brazil** at **praiasmart.com**. Each future market gets its **own section** — language-native brand, language-native domain, regionally-tuned data sources. Same tech stack, same playbook, separate front-end identities.

## Phase 0 — Brazil (2026, now)

- **Brand:** praia smart
- **Domain:** praiasmart.com
- **Language:** Portuguese (BR)
- **Beaches:** 12 live → 23 (top-20 BR) → 50+ by end of year
- **Data sources:** Open-Meteo, INEA, CETESB, INEMA, CPRH, SEMACE, IMA-AL, IMA-SC, FEPAM, INMET, YouTube cams
- **Monetization:** Phase 1-3 venue placement (free directory → claim flow → R$500/mo featured slots)
- **Year-end target:** ~50 paying venues, R$25k/mo recurring, prove the model

## Phase 1 — Portugal + Cape Verde (2027 H1)

- **Brand:** praia smart (same — Portuguese-speaking)
- **Domain:** praiasmart.pt (Portugal) + praiasmart.cv (Cape Verde)
- **Language:** Portuguese (PT-PT)
- **Beaches:** Lisboa coast, Algarve, Açores, Madeira → ~30 beaches Y1
- **Data sources:**
  - Weather: Open-Meteo, IPMA (Instituto Português do Mar e da Atmosfera)
  - Water quality: **EU Bathing Water Directive** open data via SNIRH + EEA aggregated API
  - Cams: YouTube + Portuguese surf cam networks (Beachcam.pt)
- **Monetization:** same playbook, EU-rates (€100-300/mo per venue)
- **Why first:** zero translation cost, EU data is *mandated* open, summer overlaps with BR winter (engineering team always busy)

## Phase 2 — Argentina + Uruguay (2027 H2)

- **Brand:** **playa smart**
- **Domain:** playasmart.com.ar (Argentina), playasmart.com.uy (Uruguay)
- **Language:** Spanish (rioplatense voice)
- **Beaches:** Mar del Plata, Punta del Este, Pinamar, Villa Gesell, Cariló, Necochea → ~20 beaches
- **Data sources:**
  - Weather: Open-Meteo, SMN Argentina
  - Water quality: **OPDS Buenos Aires** + Uruguayan DINAMA — regulatory data, weaker than EU
  - Cams: YouTube + Argentine cam networks
- **Why second:** **inverted seasons** — Dec-March in BR is winter in BR, but ARG/URU peak summer is Dec-March. Same calendar, same team. Same content production schedule.

## Phase 3 — Mediterranean (2028)

Three sister brands launching together, sharing one tech stack:

### Italy
- **Brand:** **spiaggia smart**
- **Domain:** spiaggiasmart.it
- **Language:** Italian
- **Beaches:** Sicilia, Sardegna, Costiera Amalfitana, Versilia, Salento → 40+ beaches
- **Data sources:** ARPA (regional environmental agencies), ISPRA, EEA Bathing Water

### Malta — *the lighthouse market*
- **Brand:** **bajja** (Maltese) OR keep `spiaggia smart` since Italian is widely spoken
- **Domain:** bajja.mt or beach.mt
- **Language:** English + Maltese + Italian (trilingual site, English primary)
- **Beaches:** ~40 official beaches — **whole country covered in 6 weeks**
- **Data sources:** ERA Malta (Environment & Resources Authority), EEA Bathing Water
- **Why Malta:** small enough to own entirely; 2.5M tourists on 500k population; premium beach-club economy (€15-30 cocktails); year-round season; English-speaking startup ecosystem; **first non-BR success story we can market**

### France (Côte d'Azur + Atlantique)
- **Brand:** **plage smart**
- **Domain:** plagesmart.fr
- **Language:** French
- **Beaches:** Côte d'Azur, Atlantic coast (Biarritz, La Baule), Corsica → 30+
- **Data sources:** Météo France, ARS regional health authorities (water quality), EEA

### Spain + Balearics (parallel with above if bandwidth allows)
- **Brand:** **playa smart** (same as ARG — Spanish global brand)
- **Domain:** playasmart.es
- **Language:** Spanish (Castilian)
- **Beaches:** Costa Brava, Costa del Sol, Balearics, Canarias → 50+
- **Data sources:** AEMET, MITECO water quality, EEA

### Greece + Cyprus
- **Brand:** **paralia** (παραλία)
- **Domain:** paralia.gr / paralia.cy
- **Language:** Greek + English
- **Beaches:** Cyclades, Crete, Cyprus → 30+
- **Data sources:** HCMR, EEA Bathing Water

## Phase 4 — Tourism arbitrage markets (2029)

Wrapper brands targeting English-speaking tourists, not locals:

- **Caribbean** — playa smart (Spanish Caribbean), separate plage smart (FR Caribbean), or unified English brand for Aruba/St. Martin/Barbados
- **Mexico tourism corridor** — playa smart (Tulum, Cancún, Playa del Carmen, Los Cabos)
- **Southeast Asia** — English wrapper for Bali, Phuket, Boracay, Goa
- **Greek islands** (overlap with Phase 3)

## Phase 5 — Mature competitor markets (2030+)

Only with funding. These have entrenched players:

- **US (California, Florida, Hawaii)** — Beach Forecast etc. exist
- **Australia** — Beachsafe is the standard; would need to out-product
- **UK + Cornwall** — Surfline UK + RNLI water-quality data dominate

## Cross-cutting infrastructure (built once, used by all)

What every regional brand inherits from the BR playbook:

1. **Same Python build pipeline** — i18n is just per-locale string lookup
2. **Same data adapter pattern** — each market's worker fits the unified `{beach_id: entry}` schema
3. **Same UI components** — sun arc, hourly strip, água box, agito meter
4. **Same monetization model** — free directory → claim → featured slot
5. **Same content cadence** — weekly city pages, daily auto-videos in season
6. **Same SEO foundation** — schema.org, FAQ schema, breadcrumbs all locale-aware
7. **Same parent infrastructure** — Cloudflare DNS, GitHub Actions cron, shared analytics

What changes per market:
- Language strings (titles, descriptions, FAQ template)
- Data sources (regional agencies + national weather)
- Cam URLs per beach
- Brand wordmark (praia/playa/spiaggia/plage/paralia/bajja)
- Cultural voice (carioca → rioplatense → siciliano → niçoise → cycladic)

## North star revisited

Original: *"praia smart becomes a verb in Brazil."*

Multi-market: ***each regional brand becomes a verb in its market.***

> *"Olha no praia smart antes de ir."* (carioca)
> *"Mirá en playa smart antes de ir."* (rioplatense)
> *"Guarda lo spiaggia smart prima di andare."* (italian)
> *"Regarde plage smart avant d'y aller."* (french)
> *"Check bajja before you go."* (maltese-english)

Same verb, six languages, one company underneath.

## Timeline pressure

| 2026 | Brazil — prove model | 50 paying venues |
| 2027 | PT-Atlantic + ARG/URU | 200 paying venues, 2nd language |
| 2028 | Mediterranean (4 markets at once) | 500 venues, 5 brands live |
| 2029 | Tourism arbitrage | 1000 venues, 8 markets |
| 2030 | Mature markets (with funding) | enterprise tier active |

**Realistic ARR trajectory** (venues @ avg $100/mo equivalent across markets):
- 2026 EoY: ~$60k ARR
- 2027 EoY: ~$240k ARR
- 2028 EoY: ~$600k ARR
- 2029 EoY: ~$1.2M ARR
- 2030: $5M+ ARR (with funding inflection)

## Decision needed in 2026

Whether to incorporate now in a structure that supports multi-market operation:
- Brazilian LLC ("Litoral Mídia Ltda" or similar) owning all the per-country brands
- Or US/Delaware C-corp owning the global rollout (necessary for VC funding eventually)
- Or Cyprus/Malta holding company (EU-tax-efficient if Mediterranean grows fast)

Decision can be deferred until first $25k/mo recurring is real. Until then it's premature.
