# SEO plan — what's done, what's parked

## ✅ Shipped (foundation layer)

- Per-page **title tags** rewritten for search intent — include "hoje", "agora", concrete keywords (mar, vento, água, câmera ao vivo)
- Per-page **meta descriptions**
- **Open Graph + Twitter cards** with YouTube cam thumbnail as og:image (changes throughout day automatically)
- **Canonical URLs** pointing to praiasmart.com (NOT .com.br — fixed)
- **sitemap.xml** with 25 URLs (homepage, sobre, melhores, 12 beaches, 10 city pages)
- **robots.txt**
- **schema.org JSON-LD**: BeachWeather per detail page, WebSite + SearchAction on homepage
- **"Sobre esta praia" sections** — 12 hand-written ~150-word PT-BR blurbs per beach (real prose, not generated)
- **Weekly city pages** — `/rio/fim-de-semana.html` etc. for 10 cities, auto-updating dates, internal-link grid on homepage

## 🟡 User-action items (pending Pedro)

- **Google Search Console verification**
  - Site: praiasmart.com (live via Cloudflare)
  - Steps: search.google.com/search-console → Add property → URL prefix → enter `https://praiasmart.com` → pick HTML tag verification → paste the meta tag to Claude → Claude ships it → click Verify → submit sitemap
- **Bing Webmaster Tools** — same drill (gets Yahoo + DuckDuckGo)
- **Plausible signup** — script is in <head> but no account exists yet. Sign up at plausible.io or swap to Umami / GoatCounter
- **First backlink** — draft post ready in earlier chat for r/rio. Personal weekend-project framing, not corporate. Don't go to r/brasil first.

## 🟡 Open eng work (queued)

- **FAQ schema** per beach (questions: "O mar tá próprio pra banho em X hoje?", "Qual o melhor horário pra surfar em Y?"). Google may render as expandable Q&A.
- **Image alt text** on cam embeds and all imagery
- **Internal linking** between nearby beaches ("perto daqui: Copa, Leblon, São Conrado")
- **News filter cleanup** — substring matching produces noise. Real fix: small LLM classifier
- **Lighthouse audit** — never run; catches render-blocking + CLS issues
- **hreflang for EN** — only if/when we add English pages for tourists

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
