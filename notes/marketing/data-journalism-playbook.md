# Data-journalism playbook (Machine 1, detailed)

The full operating detail for the data-journalism flywheel. Strategy summary is in `autonomous-growth.md`; this is the turnkey how-to.

## Why this works

We assemble balneabilidade + conditions data nobody else has in one place. Journalists need timely, local, data-backed story material and rarely have the data pipeline. We hand them a finished story. They publish + cite us → backlinks (our #1 missing ranking signal) + a referral traffic spike + third-party credibility. Repeatable every quarter, plus reactive hits.

## The report artifact

**URL pattern:** `/relatorios/estado-das-praias-{YYYY}-{Q}.html` (e.g. `/relatorios/estado-das-praias-2026-q2.html`)

**Structure:**
1. **Headline finding** — the one shareable stat ("X% das praias monitoradas do Rio ficaram impróprias pelo menos uma vez no trimestre")
2. **Ranking tables** (real data, sortable):
   - As 10 praias mais limpas (lowest avg E.coli / enterococci)
   - As 10 mais sujas / mais vezes impróprias
   - Maiores melhorias e pioras vs trimestre anterior
3. **Per-state breakdown** — RJ, SP, SC, BA, RN, PE, CE, AL (whatever we cover)
4. **Charts** — inline SVG: trend lines, bar comparisons, a "semáforo" calendar heatmap per beach
5. **Methodology box** — data sources (INEA, CETESB, INEMA...), CONAMA 274 standard, sampling cadence, our aggregation method. Transparency = credibility.
6. **Downloadable CSV** — journalists love raw data they can re-chart. Also a backlink magnet.
7. **Quote-ready lines** — pre-written sentences journalists can lift verbatim (lowers their effort = higher publish rate)
8. **Attribution ask** — "dados: praia smart (praiasmart.com)" + a linkback request

**Cadence:**
- Quarterly flagship: Jun, Sep, Dec, Mar
- Monthly mini ("balneabilidade do mês"): lighter, one chart, steady content
- Reactive: dramatic flip (a famous beach goes imprópria during a holiday) → same-day blurb + pitch

## Journalist CRM schema

Store as `data/crm/journalists.json` (or a Google Sheet via API). One record per contact:

```json
{
  "name": "...",
  "outlet": "G1 Rio",
  "beat": "cidade / meio ambiente / tech",
  "email": "...",
  "twitter": "...",
  "region": "RJ",
  "status": "cold | pitched | opened | replied | published | declined",
  "last_touch": "2026-06-15",
  "next_action": "follow-up day 3",
  "coverage": [{"date":"...","url":"...","backlink":true}],
  "notes": "prefers data exclusives; responds to WhatsApp"
}
```

**Target outlets (build this list out):**
- **National tech/data:** UOL Tilt, TechTudo, Olhar Digital, Canaltech
- **Rio:** G1 Rio, O Globo (cidade + meio ambiente), Extra, Veja Rio
- **SP:** G1 SP, Folha cotidiano, Estadão metrópole
- **Northeast:** G1 PE/CE/RN/BA, Diario de Pernambuco, O Povo (CE), Tribuna do Norte (RN)
- **Sul:** G1 SC, NSC Total, Diário Catarinense
- **Environment-specific:** ((o))eco, Mongabay Brasil, ClimaInfo
- **Aggregators:** Catraca Livre, Hypeness (share-friendly)

## Pitch email template

**Subject options (A/B these):**
- `Dados exclusivos: as praias mais (e menos) limpas do Rio neste trimestre`
- `{Beach} ficou imprópria {N} vezes em 3 meses — relatório com os dados`

**Body:**
> Oi {nome},
>
> Sou da praia smart (praiasmart.com), uma plataforma que monitora condições e balneabilidade de praias no Brasil em tempo real, puxando dados oficiais do {INEA/CETESB/INEMA}.
>
> Compilamos os últimos 3 meses e achamos alguns números que podem render uma boa pauta pra {outlet}:
>
> - {headline finding — ex: "9 das 12 semanas, Boa Viagem esteve imprópria pra banho"}
> - {second stat}
> - {a positive/surprising stat}
>
> Tenho o relatório completo com tabelas, gráficos e a planilha de dados crua, livre pra usar com crédito. Posso te mandar agora ou te passar um recorte específico de {region}.
>
> O link: praiasmart.com/relatorios/{slug}
>
> Qualquer coisa tô à disposição — inclusive pra uma fala rápida se ajudar.
>
> Abraço,
> {Renata / nome}
> praia smart · praiasmart.com

**Rules:**
- Lead with the data hook, not the company
- Offer the CSV (lowers their effort, earns the backlink)
- Regional outlets get the regional cut, not the national report
- Keep under 150 words — journalists skim

## Follow-up sequence
- Day 0: pitch
- Day 3: "te mando o recorte de {region}?" (offer, don't nag)
- Day 8: new angle / a fresher data point
- Day 14: drop, mark `declined`, re-pitch next quarter

## Distribution beyond direct pitch
- Cross-post the report to Medium / LinkedIn article (canonical back to us)
- Tweet the headline chart (taggable, journalists watch Twitter)
- Submit to r/brasil / r/rio as "fiz um levantamento dos dados de balneabilidade" (data posts do well, less spammy than product posts)
- Email digest subscribers get it first (rewards the list)

## Owner split
- **Claude:** data aggregation, report page, charts, CSV, press release, pitch drafts, CRM upkeep, follow-up drafts, coverage tracking
- **Human (or email API):** the send; any live journalist interview
- **Tier-1 (email API connected):** Claude sends + tracks + follows up; human reviews weekly

## Success metric
- Q2 (Jun): 1 published mention + 1 backlink = success (first one is hardest)
- Q3 (Sep): 3 mentions, 2 backlinks
- Q4 (Dec, "balanço do verão"): 5+ mentions, a major-outlet hit, traffic spike
