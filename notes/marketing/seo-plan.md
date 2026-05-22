# SEO plan — what's done, what's parked

## ✅ Shipped (foundation layer)

- Per-page **title tags** rewritten for search intent — include "hoje", "agora", concrete keywords (mar, vento, água, câmera ao vivo)
- Per-page **meta descriptions**
- **Open Graph + Twitter cards** with YouTube cam thumbnail as og:image (changes throughout day automatically)
- **Canonical URLs** pointing to praiasmart.com (NOT .com.br — fixed)
- **sitemap.xml** with **37 URLs** (homepage, sobre, melhores, 12 beaches, 10 city pages, 12 webcam pages)
- **robots.txt**
- **schema.org JSON-LD**: BeachWeather + FAQPage + BreadcrumbList + VideoObject per detail page, WebSite + SearchAction on homepage
- **"Sobre esta praia" sections** — 12 hand-written ~150-word PT-BR blurbs per beach (real prose, not generated)
- **Weekly city pages** — `/rio/fim-de-semana.html` etc. for 10 cities, auto-updating dates, internal-link grid on homepage
- **FAQ sections + FAQPage schema** — 5 parameterized PT-BR Q&A per beach, `<details>` accordion + JSON-LD (shipped in 7-item sprint, commit 4d45f66)
- **BreadcrumbList JSON-LD** — on detail, city, and webcam pages
- **VideoObject JSON-LD** — per live cam (eligible for Google video search)
- **"Praias próximas" internal linking** — every detail/city/webcam page links to 3 nearest beaches (haversine)
- **12 webcam landing pages** — `/copacabana/webcam-ao-vivo.html` etc., targets high-volume "webcam X ao vivo" searches
- **Lazy-loaded YouTube iframes** — `loading="lazy"` + referrer-policy (Core Web Vitals win)
- **Preconnect hints** — i.ytimg, youtube, fonts (faster first paint)
- **Favicon** — coral half-sun SVG
- **Footer with data-source citations** — outbound links to INEA/CETESB/INEMA/Open-Meteo/INMET (E-E-A-T signal)

## 🟡 User-action items (pending Pedro)

- **Google Search Console verification**
  - Site: praiasmart.com (live via Cloudflare)
  - Steps: search.google.com/search-console → Add property → URL prefix → enter `https://praiasmart.com` → pick HTML tag verification → paste the meta tag to Claude → Claude ships it → click Verify → submit sitemap
- **Bing Webmaster Tools** — same drill (gets Yahoo + DuckDuckGo)
- **Plausible signup** — script is in <head> but no account exists yet. Sign up at plausible.io or swap to Umami / GoatCounter
- **First backlink** — draft post ready in earlier chat for r/rio. Personal weekend-project framing, not corporate. Don't go to r/brasil first.

## 🟡 Open eng work (queued)

- **Image alt text** on cam embeds and all imagery (still TODO)
- **Lighthouse audit** — never run; catches render-blocking + CLS issues
- **hreflang for EN/multi-locale** — needed when i18n lands for 2027 expansion
- **News filter** — keyword precision improved (word-boundaries + blocklist, commit 52cdd76), BUT news ticker not currently rendered in UI. Real precision ceiling still needs the LLM classifier when ticker returns.

### ✅ Recently cleared from this list
- ~~FAQ schema per beach~~ → shipped (4d45f66)
- ~~Internal linking between nearby beaches~~ → shipped as "praias próximas" (4d45f66)
- ~~News filter cleanup~~ → keyword fix shipped (52cdd76); LLM classifier still parked

## Strategic SEO bets (when we have traffic data)

- **More city pages** — go beyond `fim-de-semana`. Add `/rio/agora.html`, `/rio/amanha.html`, `/rio/feriados.html`
- **Long-tail beach combinations** — `/copa-vs-ipanema/` comparison pages (massive search volume)
- **Seasonal landings** — `/reveillon-copacabana-2026.html`, `/carnaval-praias-2027.html` — these RANK because they're hyper-specific
- **Linkbait pieces** — "as 10 praias mais limpas do Rio em 2026" with real data table, sharable, journalist-friendly

## Realistic timeline

- **Week 1 after launch**: Google starts crawling, sitemap discovered
- **Week 2-4**: First impressions in Search Console (maybe 20-100/day)
- **Month 2-3**: Real ranking positions visible, click-through data
- **Month 4-6**: Compounding effect kicks in IF we keep publishing content
- **Dec-Feb high season**: traffic should be 5-10× whatever month 6 looks like

SEO is a delayed-reward game. Foundation is laid; what matters now is consistency + backlinks + summer-season-targeted content.
