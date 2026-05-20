# Brand architecture

## Decision made

We go with **Option C — holding company with localized sister brands.**

Each market gets a native-language brand on a country-specific domain. They look like siblings to a user (familiar logo system, familiar UI), but each is the *native* thing in its own market — not an imported translation.

Underneath, one tech stack, one team, one playbook.

## The brand family

| Market | Brand wordmark | Domain | Voice |
|---|---|---|---|
| Brasil | **praia smart** | praiasmart.com | carioca / praiano |
| Portugal | **praia smart** | praiasmart.pt | tuga, slightly more formal |
| Cape Verde | **praia smart** | praiasmart.cv | morabeza / cape verdean PT |
| Argentina | **playa smart** | playasmart.com.ar | rioplatense, voseo |
| Uruguay | **playa smart** | playasmart.com.uy | rioplatense |
| Chile | **playa smart** | playasmart.cl | chileno, slang-aware |
| España | **playa smart** | playasmart.es | castellano |
| México | **playa smart** | playasmart.mx | mexicano |
| Italia | **spiaggia smart** | spiaggiasmart.it | italiano, regional accents respected |
| France | **plage smart** | plagesmart.fr | français, riviera tone |
| Grecia | **paralía smart** | paralia.gr | greek + english |
| Malta | **bajja smart** | bajja.mt | english + maltese + italian (trilingual) |

## Visual identity (consistent across all brands)

What stays the same everywhere:
- **Color palette** — coral (#E8895E), sea-blue (#5A9FB5), sand-gold (#E5B86A), sage (#7C9183), paper (#F4EFE4), ink (#1F3F4D)
- **Typography** — Instrument Serif (italic, wordmark first word) + Plus Jakarta Sans (bold, wordmark second word) + JetBrains Mono (data labels)
- **The half-sun-over-wave glyph** — abstract mark that doesn't depend on language
- **The light, breezy, "beach at 10am" aesthetic** — across all markets
- **UI components** — sun arc dials, hourly strip, água box, agito meter, parasol crowd indicator

What changes per brand:
- The first word of the wordmark (praia / playa / spiaggia / plage / paralía / bajja)
- "smart" stays "smart" everywhere (universal, short, technical credibility)
- Locale-specific iconography (Argentine *bañado*, Italian *ombrelloni* lineup, Maltese *luzzu* boat — subtle cultural details)
- Per-market hero photography mood (Mediterranean blue vs Atlantic coral vs Caribbean turquoise)

## Why not Option A (totally separate brands)

A single parent identity ("Coastly", "Litoral", "Tide") would lose the *native* feel. The whole point of "praia smart" working in Brazil is that *praia* is the word Brazilians actually use. A foreign English-derived name would feel like the imported product it would be.

## Why not Option B (totally localized, no shared parent)

Marketing budget would fragment. Press coverage of one brand wouldn't help the others. Investor pitch would be "we operate twelve unrelated apps" — terrible story. Tech debt would multiply if each brand drifted in implementation.

## The legal / corporate structure (defer until 2027)

Until first $25k/mo recurring is real, we operate as one business. After that:

**Recommended structure** (when forced to decide):
- **Parent holding company** in a tax-favorable jurisdiction (Delaware C-corp if going VC route; Cyprus/Malta if going organic Mediterranean-heavy; Portuguese Madeira free-trade if going EU-EU route)
- **Operating subsidiaries** per major market:
  - Brazilian Ltda → owns praiasmart.com.br / praiasmart.com operations
  - Spanish SL → owns playasmart.es, playasmart.com.ar (or Argentine SRL)
  - Italian SRL → owns spiaggiasmart.it + bajja.mt
- **Centralized IP** in parent — codebase, brand marks, customer data
- **License-back model** — parent licenses brand + tech to each subsidiary for a fixed royalty (transfer-pricing legitimate, used by Spotify, Booking, others)

This is a year-2+ problem. Don't lawyer it now.

## Domain acquisition strategy

**Snap up cheap defensive domains NOW** (before any market launch):
- praiasmart.pt, praiasmart.cv (€20-50 each via Registro.pt / Punto.cv)
- playasmart.com.ar, playasmart.com.uy, playasmart.cl, playasmart.es, playasmart.mx (~$10-30 each)
- spiaggiasmart.it, plagesmart.fr (~€15 each)
- paralia.gr (~€20)
- bajja.mt (~€50)

Total: ~$300 USD for the entire global domain portfolio. Cheaper than one Friday-night out, locks the brand family forever.

**Watch out for:**
- praiasmart.com.br — Brazilian .com.br ccTLD. Probably should grab as defensive (R$40/yr).
- praia.com / playa.com — likely premium domains worth $$$. Skip unless someone hands us VC money.

## Wordmark + glyph spec

Every brand follows this pattern:
```
{native word for beach} smart   [half-sun-over-wave glyph]
   ↑ italic serif                ↑ same glyph everywhere
                ↑ bold sans-serif (always "smart")
```

The mark family looks like a published periodical's masthead — *praia smart* alongside *playa smart* feels like *The Atlantic* alongside *The Atlantic Daily*: clearly siblings, each with its own job.

## Localization tech requirements

To support this from one codebase:
- Add a `locale` config per generator (PT-BR, PT-PT, ES-AR, ES-ES, IT, FR, EL, MT-en)
- Move all user-facing strings into a `locales/{locale}.json` lookup
- Per-locale brand wordmark + domain in the head/footer
- Per-locale FAQ template (translated answers, same questions)
- Per-locale "sobre esta praia" content (translation OR re-write — translation usually fine for stub content)
- Per-locale date formatting (`5 de janeiro` vs `5 enero` vs `5 gennaio`)
- Per-locale `<html lang>` attribute and og:locale meta

**Effort to add a new locale, given the infrastructure exists:** ~2 weeks per market, dominated by data-source integration (state agency parser), not translation.

## What we tell partners / press

Single sentence:

> *"We're building the decision layer for the beach economy — one local brand per market, one platform underneath."*

Carries the *local* respect we need to win each individual market, and the *scale* story we need for funding when the time comes.
