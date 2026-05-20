# Launch checklist — winter 2026 → summer 2026/27

Site is **live** at praiasmart.com (Cloudflare). Working through pre-busy-season polish before the Dec push.

## ✅ Done

- Light "praia 10am" UI redesign across all page types
- Live cams + conditions + tides + crowd estimates for 12 beaches
- INEA Rio água-limpa data via XLSX (7/7 Rio beaches)
- CETESB, INEMA, CPRH, SEMACE, IMA-AL, IMA-SC, FEPAM workers
- Dynamic top-4-of-10 dial system per beach
- Dedicated água box with status + age + rain overlay
- Sun arc score viz, hourly strips, parasol crowd meters, sunset hero card
- 12 hand-written beach descriptions (PT-BR)
- 10 weekly city pages (`/{city}/fim-de-semana.html`)
- Ads via A-Ads (unit 2438146, homepage cards + 2 per detail page)
- SEO foundation (titles, meta, OG, canonical, sitemap, schema.org)
- Plausible analytics script (no account signed up yet)
- Deploy via GitHub Actions every 15 min

## 🟡 User-action items (Pedro)

- [ ] Google Search Console verification (see `marketing/seo-plan.md`)
- [ ] Bing Webmaster Tools setup
- [ ] Plausible account signup
- [ ] First backlink push (r/rio draft ready in chat history)
- [ ] Fact-check 4 beach descriptions (Rincão emancipation year; Santos Gonzaga Guinness garden; Praia Grande "Eye" Ferris wheel; Copa P5 phrasing)
- [ ] Phone QA pass — open all 12 beach pages + 10 city pages on real iPhone + cheap Android

## 🟡 Open eng work (queued)

- [ ] News filter cleanup (substring matching is noisy)
- [ ] Lighthouse / perf audit (mobile-first)
- [ ] Cams for 11 new top-20 beaches (Ipanema, Barra, Boa Viagem, Pajuçara, Iracema, Jurerê, Porto de Galinhas, Itapuã, Geribá, Tramandaí, Porto Seguro) — água data already wired
- [ ] INEMA worker quirk: geo-blocked PDFs, currently uses news article (no E.coli numbers)
- [ ] IMA-SC seasonal: verify in October when in-season data resumes
- [ ] Vai dar Praia + Semace Digital app API sniffs (both attempted, no public JSON found — retry later)

## 🟡 Bonus integrations parked (stub workers exist)

- [ ] Orla Rio bandeiras (lifeguard flags) — needs CV on cam frames
- [ ] Observatório do Turismo calibration — needs per-state PDF/XLSX parsers
- [ ] LAPIS/UFAL satellite supplement — needs EUMETSAT WMS layer ID

## 🔴 Monetization (separate roadmap — see business/)

- [ ] Phase 1: free directory of beachside venues (10 per beach)
- [ ] Phase 2: owner-claim flow (captures emails)
- [ ] Phase 3: featured paid placement at R$500/mo per slot
- [ ] Outreach via Renata email template once we have traffic data
- [ ] TikTok auto-video bot (parked for Dec — see `tiktok-bot.md`)

## Timeline pressure

- **May 2026 (now)**: winter low season. Time to polish without traffic pressure.
- **Aug-Sep 2026**: pre-season ramp. SEO content push, finalize venues, Phase 1.
- **Oct-Nov 2026**: pre-busy push. Phase 2 owner claims, start sales calls.
- **Dec 2026 - Feb 2027**: BUSY SEASON. Site must work flawlessly under load. TikTok bot active. Featured slots monetizing.
- **Mar 2027 +**: review what worked, plan next year.
