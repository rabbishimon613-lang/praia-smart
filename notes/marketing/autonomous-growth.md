# Autonomous growth plan — Claude-run machines

The strategy: build growth **machines** Claude operates end-to-end, where the only human input is final-send auth (or an API key that removes even that). Most growth work is research → draft → personalize → follow-up → measure. That grind is free with Claude. Humans do identity-bound things (face, voice, signature, payment, account login).

This doc has: the 6 machines, each with a workflow + cadence + owner split + tooling, then a month-by-month timeline (May 2026 → Feb 2027), metrics, decision gates, and the infrastructure to wire up.

---

## Operating principle

> Claude **captures** demand (SEO, programmatic pages) AND **creates** demand (data journalism, outreach, recurring content). The multiplier is connecting two APIs — one email sender, one social scheduler — which converts Claude from "drafts everything" to "runs everything, you review a weekly digest."

Two tooling tiers:

- **Tier 0 (no setup):** Claude builds pages/content/drafts. Human copy-pastes or clicks send.
- **Tier 1 (two API keys):** email API (Resend/SendGrid/Gmail API) + social scheduler (Buffer/Postiz/Ayrshare). Claude sends + posts + tracks autonomously. **This is the unlock — prioritize wiring it in June.**

---

## Machine 1 — Data-journalism flywheel

**What:** Turn our balneabilidade + conditions data into newsworthy reports that earn backlinks, press, and traffic from a single artifact. Repeatable quarterly.

**Why it's #1:** It's the only tactic that hits backlinks + press + traffic + credibility simultaneously. We genuinely own data nobody else has assembled. Journalists *want* this.

### Workflow
1. **(Claude)** Aggregate 90 days of balneabilidade.json + conditions history → compute rankings: cleanest/dirtiest beaches, most-improved, worst-offenders, "X flipped imprópria N times this summer"
2. **(Claude)** Write the report as a standalone page: `/relatorios/estado-das-praias-{quarter}.html` — charts (inline SVG), data tables, methodology, downloadable CSV
3. **(Claude)** Write a tight press release + a personalized pitch email per journalist (real hook: "Boa Viagem foi imprópria em 9 das 12 semanas — temos os dados")
4. **(Claude)** Maintain journalist CRM: G1 Rio/SP/NE desks, UOL Tilt, TechTudo, Catraca Livre, Folha, Estadão local, regional outlets per market
5. **(Human or API)** Send pitches
6. **(Claude)** Track opens/replies, draft follow-ups, log coverage + resulting backlinks

### Cadence
- Quarterly flagship report (Jun, Sep, Dec, Mar)
- Monthly mini-data-posts ("balneabilidade do mês") for steady content
- Reactive: when a beach has a dramatic flip, instant data blurb + pitch

### Owner split
- Claude: 95% (data, report, charts, release, pitch list, follow-ups)
- Human: send auth (Tier 0) or nothing (Tier 1)

---

## Machine 2 — Outreach engine

**What:** A standing, always-on outreach system across four audiences, each with its own CRM, message templates, and follow-up sequences.

### The four pipelines

| Pipeline | Audience | Goal | Volume target |
|---|---|---|---|
| Sales | Beachside venues | Paid featured slots | 200 contacted by Dec |
| PR | Journalists | Backlinks + press | 50 |
| Partnerships | Hostels, pousadas, surf schools, dive shops | Cross-promo | 100 |
| Seeding | Micro-influencers | Honest posts/stories | 40 |

### Workflow (per pipeline)
1. **(Claude)** Build + maintain CRM (JSON in repo, or Google Sheet via API): name, contact, beach, hook, status, last-touch, next-action
2. **(Claude)** Research contacts (WebSearch + WebFetch). Honest about email-scarcity for BR SMBs — flag low-confidence, suggest substitutes
3. **(Claude)** Draft personalized email per target with a real data hook (Renata voice for sales — see `sales/outreach-email-renata.md`; different voice per pipeline)
4. **(Claude)** Build multi-touch sequence: send → day-3 WhatsApp/email nudge → day-7 new angle → day-14 drop
5. **(Human or API)** Send
6. **(Claude)** Log responses, advance pipeline stage, schedule follow-ups, surface hot leads for Shimon's calls

### Cadence
- Weekly batch: Claude preps ~30 personalized drafts, queued for review
- Daily (Tier 1): Claude sends scheduled follow-ups, updates CRM

### Owner split
- Claude: research, draft, personalize, sequence, track
- Human: send (Tier 0), the actual sales *calls* (always human — see `sales/call-script-shimon.md`), payment handling

---

## Machine 3 — Recurring content products (build returning audience)

**What:** Owned-audience channels so we're not renting every visit from Google. Habit beats one-time traffic.

### 3a. Weekly "fim de semana" email digest
- **Workflow:** (Claude) every Friday AM, generate digest from data — top beaches for the weekend per region, água alerts, best windows → render HTML email → send to list via API
- **List building:** a "receba as condições no seu email" signup on every page (Claude builds the form → stores to a JSON/Sheet/email-API audience)
- **Cadence:** Friday mornings, year-round; daily during summer peak
- **Owner:** Claude end-to-end once email API connected

### 3b. Daily auto-social (the TikTok bot + siblings)
- **Workflow:** (Claude) render vertical video per top beach (ffmpeg + cam still + TTS + overlays — see `tiktok-bot.md`), write caption + hashtags, push to scheduler queue
- **Cadence:** Sep onward ramp; daily for top-5 beaches by Dec; instant água-imprópria alerts
- **Owner:** Claude renders + queues; human connects scheduler API (Ayrshare/Postiz handle TikTok+IG+Twitter from one call)

### 3c. WhatsApp broadcast
- **Workflow:** (Claude) generate the daily/weekend message; broadcast to opt-in subscribers
- **Note:** WhatsApp Business API has cost + approval friction. Phase this in only if the email + social channels prove the content resonates. Brazil-critical channel though — worth it eventually.

---

## Machine 4 — Distribution seeding (low-glamour, compounds)

**What:** Get our links + presence onto sites that already have authority + traffic.

### Workflow
1. **(Claude)** Draft Wikipedia citations — pt.wikipedia beach articles ("Copacabana", "Praia de Ponta Negra") can cite live-conditions external links. Draft the edit + citation. **(Human)** reviews + submits (Wikipedia bans undisclosed automated edits — must be human-posted, genuinely useful)
2. **(Claude)** Find + draft submissions to directories: travel guides, surf-spot databases, "o que fazer em {cidade}" listicles, Google Business-adjacent beach listings
3. **(Claude)** Monitor (via scheduled WebSearch) Reddit/Quora/forum questions like "como tá o mar em copacabana hoje" → draft a genuinely helpful answer linking the right page → **(Human)** posts from a real account
4. **(Claude)** Syndicate the data-journalism reports to Medium, dev.to, LinkedIn articles (cross-post, canonical back to us)

### Cadence
- Weekly: 3-5 new seeding actions drafted
- Reactive: forum-question monitoring runs as a scheduled task

---

## Machine 5 — Programmatic SEO (the floor)

**What:** Hundreds of long-tail pages from data we already have. Compounds forever, zero human input. The base layer everything stands on.

### Page types to generate
- `/copa-vs-ipanema` and all viable beach-pair comparisons (high search volume)
- `/reveillon-copacabana-2027`, `/carnaval-praias-rio-2027`, `/feriado-{x}-praias` seasonal landings (need lead time to rank — build by Sep)
- "O mar tá bom em {beach} hoje?" Q&A pages
- "Melhores praias pra {família/surfar/criança/cachorro} em {cidade}" ranking pages
- `/glossario` (balneabilidade, ressaca, swell, agito...)
- Per-beach: `/agora`, `/amanha` variants alongside existing `/fim-de-semana` + `/webcam-ao-vivo`

### Workflow
- (Claude) build generators, wire into the 15-min cron, extend sitemap
- Freshness signal already strong (15-min rebuild) — Google crawls often

### Cadence
- One new page-type per week through winter (May-Aug)
- All seasonal pages live by end of Sep (lead time to rank before Dec)

---

## Machine 6 — Product-as-distribution

**What:** Make the product itself spread.

### 6a. Share-card generator (highest-priority build)
- (Claude) one-tap "compartilhar" → renders a branded condition card image (beach + conditions + água + watermark) → WhatsApp/IG/copy-link
- Turns every user into a distributor. Build first — it's the viral substrate everything else feeds.

### 6b. Água-imprópria auto-broadcast
- (Claude) the moment a beach flips imprópria, auto-generate + fire: tweet, IG story, TikTok script, alert page, push notification, WhatsApp blurb
- Public-health urgency + "eu avisei" social currency = highest organic share rate we'll ever get

### 6c. PWA + push notifications
- (Claude) manifest + service worker + opt-in push "⚠️ {beach} imprópria hoje"
- Re-engagement channel we own outright

---

## Month-by-month timeline

### May 2026 (now) — foundation
- ✅ SEO foundation + sprint #2 shipped
- [ ] Claude: build share-card generator (Machine 6a) — **top priority**
- [ ] Claude: build first seasonal pages + comparison pages (Machine 5)
- [ ] Human: wire email API + social scheduler (the Tier-1 unlock)

### June — wire the machines
- [ ] Claude: first quarterly data-journalism report (Machine 1) + journalist CRM
- [ ] Claude: build email-digest signup + generator (Machine 3a)
- [ ] Claude: build outreach CRMs + first draft batches (Machine 2)
- [ ] Human: connect APIs if not done; send first PR pitches

### July — content velocity
- [ ] Claude: programmatic SEO at 1 new page-type/week (Machine 5)
- [ ] Claude: TikTok bot renderer built + tested (Machine 3b)
- [ ] Claude: água-imprópria auto-broadcast wired (Machine 6b)
- [ ] Weekly email digest live + growing list

### August — dry run
- [ ] All machines operational, low cadence
- [ ] Claude: PWA + push (Machine 6c)
- [ ] First data report should have earned 1-2 backlinks; iterate the pitch
- [ ] Distribution seeding weekly (Machine 4)

### September — ramp begins
- [ ] All seasonal SEO pages live (lead time before summer)
- [ ] TikTok daily posting starts (algorithm warm-up)
- [ ] Outreach volume up: 30 venues + 20 partnerships contacted
- [ ] Q3 data report published + pitched

### October — pre-season push
- [ ] Outreach intensifies (sales calls begin — human)
- [ ] Influencer seeding (Machine 2 seeding pipeline)
- [ ] Email list should be 300+
- [ ] IMA-SC seasonal data resumes — refresh SC content

### November — final prep
- [ ] Everything tuned for load
- [ ] Réveillon + Carnaval pages optimized, ranking
- [ ] TikTok cadence full
- [ ] Press round 1 lands (from Q3 report + pre-season pitches)

### December–February — summer blitz
- [ ] Réveillon Copacabana real-time push (2-3M people on the beach)
- [ ] Água-imprópria auto-broadcast firing on every flip
- [ ] Daily TikTok + Reels + Shorts
- [ ] Q4 data report ("balanço do verão") + press round 2 with real traffic numbers
- [ ] Daily email digest
- [ ] Paid ads ONLY if venue revenue is flowing

---

## Metrics + decision gates

| Gate | When | Pass criteria | If fail |
|---|---|---|---|
| SEO indexing live | Jun | Search Console shows pages indexed | chase verification/sitemap issues |
| First backlink | Jul | ≥1 from data report | revise report angle + pitch |
| Email list traction | Aug | ≥100 subs, >30% open rate | rethink digest value/frequency |
| TikTok signal | Oct | ≥1k followers, ≥1 video >10k views | revise format/cadence |
| Pre-season traffic | Nov | ≥1k daily sessions | double down on what's working |
| Summer peak | Jan | ≥10k daily sessions, 1-2 viral moments | analyze, fix for next year |

## Infrastructure to wire (the Tier-1 unlock)

Priority order:
1. **Email-sending API** — Resend (cleanest dev experience, generous free tier) or SendGrid. Unlocks Machines 1, 2, 3a.
2. **Social scheduler API** — Ayrshare (one API → TikTok+IG+Twitter+FB) or Postiz (open-source). Unlocks Machine 3b + 6b.
3. **Audience store** — start with JSON in repo / Google Sheet; graduate to the email API's native audience list.
4. **(Later) WhatsApp Business API** — Brazil-critical but cost + approval friction. Phase in after email+social prove out.

Each is a single API key + a small Claude-built integration. Once in place, Claude operates the machines and surfaces a **weekly digest** of everything that went out + results, so the human reviews rather than executes.

## Failure modes to watch

- **Email deliverability** — bad sends tank domain reputation. Warm up the sending domain, never blast unverified lists, honor unsubscribes. (Why we found real venue emails matter, not guesses.)
- **TikTok automation limits** — TikTok BR may require partner status for automated uploads. Fallback: render files, human batch-uploads, or use Ayrshare (handles auth).
- **Wikipedia/forum bans** — automated link-dropping gets banned. These MUST be human-posted + genuinely useful, or skip.
- **Content sameness** — programmatic pages risk thin-content penalties. Each must carry unique real data, not template filler.
- **Spreading thin** — 6 machines is a lot. If forced to pick 3: Machine 1 (data journalism), Machine 5 (programmatic SEO), Machine 6a (share cards). Those three are nearly 100% Claude-autonomous and hit demand-creation + demand-capture + virality.

## The one-paragraph version

Claude builds and runs six growth machines. Three are pure-autonomous (programmatic SEO, share cards, data reports). Three need either a human click or one API key to go autonomous (outreach emails, recurring digests, auto-social). Wiring one email API + one social scheduler in June converts the whole system to Claude-operated, human-reviewed. Through winter we build + dry-run; September we ramp; December–February we blitz, with the água-imprópria auto-broadcast and Réveillon as the viral peaks. Total cash through summer: under R$10k, most optional. Everything is written down, repeatable, and templatable for the 2027 multi-market expansion.
