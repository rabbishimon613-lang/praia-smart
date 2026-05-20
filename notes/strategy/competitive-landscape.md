# Competitive landscape

Honest read on who else plays in the "Brazilian beach decision" space. We don't have a direct competitor doing what we're doing — but we have **adjacent overlap** in every direction.

## Adjacent players, ranked by overlap

### 1. Climatempo / Tempo Agora / Globo Tempo — weather portals
- **Strength:** dominant brand, native app installs, push notifications, daily-routine users
- **Weakness:** generic by city, no per-posto granularity, no água, no live cam, no agito, no balneabilidade
- **Threat level:** Medium-low. They could add beach features, but it's not a strategic priority for them. Their model is broad-weather, not hyperlocal beach.
- **What we steal:** People who currently check Climatempo before the beach. ~20-30% of our addressable market.

### 2. Windguru / Windy / Surfline — surf forecasts
- **Strength:** loved by surfers, technically deep (swell models, period, direction)
- **Weakness:** surf-only, gringo aesthetic, no água, no agito, ignored by non-surfers
- **Threat level:** Low. They're tightly focused on surf market and have no incentive to broaden.
- **What we steal:** Casual surfers who want surf data alongside everything else. Maybe 5-10% of audience.

### 3. INEA / CETESB / state agencies — official balneabilidade
- **Strength:** authoritative, free, comprehensive water-quality data, federal funding
- **Weakness:** PDFs from 2005, no integration, no UI, no mobile, weekly cadence
- **Threat level:** Zero. They're regulators, not product builders. They're our DATA SOURCE.
- **What we extract:** their data + the trust signal of citing them. "INEA · 4 dias atrás" = we get the credibility without being an agency.

### 4. YouTube live cams — direct streams
- **Strength:** free, real-time, no signup, embedded everywhere
- **Weakness:** fragmented (one channel per cam), no data overlay, no aggregation, no search
- **Threat level:** Zero. YouTube doesn't care about beach UX.
- **What we do:** aggregate their cams + add data overlay + make discovery easy. They're our visual layer.

### 5. Instagram beach accounts — @copacabanaonline, @ipanemavida, etc.
- **Strength:** community-curated, real photos, native to mobile, Instagram audience
- **Weakness:** vibes-only, no data, post-hoc not pre-decision, account-by-account fragmented
- **Threat level:** Low. They serve a different need (entertainment + identity), not decision-making.
- **What we coexist with:** they're our distribution channel (cross-posts, story features), not competition.

### 6. Globo G1 / UOL — news media beach coverage
- **Strength:** SEO dominance, brand trust, broad reach
- **Weakness:** episodic (weekly balneabilidade pieces), not real-time, generic
- **Threat level:** Low. They publish about beaches; they don't BE a beach app.
- **What we partner with:** ideally embedded data widgets on their beach articles. Long-term play.

### 7. State / city tourism boards — Setur RJ, Setur CE, etc.
- **Strength:** government endorsement, official maps
- **Weakness:** off-season they disappear, no real-time, design is a decade behind
- **Threat level:** Zero. They'd be ideal customers, not competitors.
- **What we sell them:** the API license eventually. "Setur CE wants to know what their tourists are doing" = enterprise tier.

### 8. Wave / GuruSurf / SurfStation — Brazilian surf apps
- **Strength:** Brazilian, mobile, niche communities
- **Weakness:** surf-only, small audiences, design dated, no integration
- **Threat level:** Low-medium. They could pivot to broader beach but it'd be a strategic shift. Worth monitoring.
- **What we coexist with:** they keep dedicated surf; we have everyone else.

### 9. Beachsafe (Australian, comparable model overseas)
- **Strength:** great example of a beach app done right (Aussie market)
- **Weakness:** Australia-only, no Brazilian presence, no plans to expand
- **Threat level:** Zero in current markets. Useful as a **product reference** — how they monetize, what features users actually use.
- **What we learn:** their app store reviews are a free user research goldmine for what beach-app users want.

## The "blind spot" map

Here's where each player has a hole we fill:

| Player | Their hole | Why they won't fix it |
|---|---|---|
| Climatempo | per-posto granularity | Their UX is built for city-level forecasts |
| Surfline | non-surf data | Surfers pay them; non-surfers don't |
| INEA / CETESB | UI + real-time + multi-source | Government, not product |
| YouTube cams | aggregation + data overlay | YouTube doesn't care |
| Instagram accounts | data + structure | They're entertainment |
| Globo G1 | freshness + interaction | They're news, not app |
| Tourism boards | continuous updates | Funded seasonally |
| Brazilian surf apps | non-surf audience | Niche identity |

We sit in the geometric center of all of them. That's the wedge.

## What could kill us

Real risks, in priority order:

### 1. Globo / UOL / Climatempo decides to ship this themselves
The mega-portals have the audience and engineering resources. If they decided beach-decision was strategic for summer 2026, they could clone us in 6 weeks. **Mitigation:** move fast, lock the venue-monetization side they can't easily replicate (corporate sales motion is slow at megacorps), and become the data-quality leader before they notice.

### 2. INEA / CETESB launches a modern app
Less likely (government, slow), but if a tech-forward minister decides to "modernize" balneabilidade, they could ship an official app that gets installed by default. **Mitigation:** make sure our value isn't just citing their data — make it the agito, the integration, the venue layer.

### 3. A YC-backed clone targets the same wedge
Some PT-speaking founder sees the gap, raises $1M, hires 5 engineers, beats us on polish. **Mitigation:** ship fast, dominate SEO before they ramp, build venue relationships that are sticky.

### 4. Cloudflare blocks us / data source disappears
We depend on Open-Meteo (global, no auth, stable), state agency PDFs (could change format), YouTube embeds (TOS could shift). **Mitigation:** keep workers defensive (already are), maintain fallback data sources, never depend on a single source for a feature.

### 5. We lose discipline and become a feature factory
Easy trap. Build the social layer, then booking, then reviews, then a chat. Quality dilutes. Brand drifts. **Mitigation:** read `positioning.md` once a month before adding any new feature.

## The competitive moat (what's actually defensible)

In order of strength:

1. **Data integration breadth** — assembling 8+ data sources is annoying. We've done it. Replicating takes 3+ months.
2. **Per-posto granularity** — manually curated cam list + state-agency mapping. Tedious to recreate.
3. **PT-BR voice + Brazilian beach DNA** — generic translation can't fake this.
4. **SEO compounding** — 25+ pages indexed, growing weekly. By month 6 we have hundreds of long-tail rankings.
5. **Venue relationships** — Phase 2 owner-claim flow gives us a small CRM. Once we have 200 verified venues, switching cost for them is real.

None of these alone are unassailable. Together they're a meaningful head start. The question is whether we use the 6-month window before someone serious shows up.
