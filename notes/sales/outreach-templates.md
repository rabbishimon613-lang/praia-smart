# Outreach templates — all pipelines

The sales pipeline (venues) has its own doc: `outreach-email-renata.md`. This covers the other three Machine-2 pipelines: **PR**, **partnerships**, **influencer seeding**. PT-BR, personalized-with-data-hook, multi-touch.

The PR/journalist pipeline template lives in `../marketing/data-journalism-playbook.md`. Below: partnerships + influencers.

---

## CRM schema (shared across pipelines)

Store as `data/crm/{pipeline}.json`:

```json
{
  "name": "...",
  "org": "...",
  "type": "venue | journalist | hostel | surf-school | pousada | influencer",
  "beach": "copa-p5",
  "contact": {"email": "...", "instagram": "...", "whatsapp": "..."},
  "hook": "real data hook personalized to them",
  "status": "cold | contacted | opened | replied | active | declined",
  "last_touch": "2026-06-15",
  "next_action": "...",
  "notes": "..."
}
```

---

## Pipeline: Partnerships (hostels, pousadas, surf schools, dive shops)

**Goal:** mutual cross-promotion. They tell their guests "check conditions on praia smart"; we send them traffic via beach pages. No money — pure barter.

**Why they say yes:** it makes them look helpful to guests, costs nothing, and a surf school *needs* condition data anyway.

### Email template

**Subject:** Parceria praia smart — condições da {praia} pros seus hóspedes/alunos

> Oi {nome},
>
> Sou da praia smart (praiasmart.com) — a gente mostra condições da {praia} em tempo real: câmera ao vivo, ondas, vento, água, melhor horário. De graça.
>
> Vi que vocês são {hostel/escola de surf/pousada} na {praia} e pensei numa parceria simples, sem custo pra ninguém:
>
> - Vocês compartilham o link da {praia} com hóspedes/alunos ("olha as condições aqui")
> - A gente destaca vocês na nossa página da {praia} como parceiro local
>
> Os seus alunos/hóspedes já querem saber como tá o mar — a gente entrega isso pronto. E vocês aparecem pra todo mundo que checa a {praia} no nosso site.
>
> Topa? Posso te mandar como ficaria.
>
> Abraço,
> {Renata / nome} · praia smart

### Follow-up
- Day 4: WhatsApp — "viu meu email sobre a parceria? Sem custo, rapidinho"
- Day 10: drop

---

## Pipeline: Influencer seeding (micro, 10k–80k followers)

**Goal:** one honest post/story from niche micro-influencers (carioca lifestyle, surf, família-praia, "rolê no Rio"). 20 micros > 1 macro: cheaper, higher trust, targeted.

**Offer:** free featured placement for their favorite beach + early access + (for the good ones) a small fee R$200-500. Mostly barter.

### DM / email template

**Subject / opener:**
> Oi {nome}! Acompanho seu conteúdo de {praia/surf/Rio} 🏖️
>
> Construí a praia smart (praiasmart.com) — um painel que mostra como tá cada praia AGORA: câmera ao vivo, ondas, água, melhor horário. Tudo de graça.
>
> Achei que tem tudo a ver com seu público. Queria te dar acesso antecipado e, se curtir de verdade, adoraria que você mostrasse pra galera — do seu jeito, sem script.
>
> Em troca: destaco a sua praia favorita no site e te dou um espaço de parceiro. Se rolar de fazer um Reels/story, a gente acerta um valor também.
>
> Posso te mandar o acesso? Qual sua praia?
>
> {nome} · praia smart

**Rules:**
- Reference their actual content (not generic blast)
- "do seu jeito, sem script" — authenticity sells better than controlled messaging
- Lead with give (access, free placement), not ask
- The água-imprópria alerts are great influencer hooks ("post isso quando a praia tá imprópria, seu público compartilha")

### Follow-up
- Day 3: "viu? qualquer dúvida tô aqui"
- Day 7: send a sample share-card of *their* beach (shows value concretely)
- Day 14: drop

---

## Pipeline notes — sequencing & cadence

- **Weekly batch:** Claude preps ~30 personalized drafts across pipelines, queued for review
- **Daily (Tier-1):** Claude fires scheduled follow-ups, updates CRM, surfaces hot leads
- **Personalization is non-negotiable:** every email needs a real, specific hook (their beach, their content, their data). Generic = spam = wasted domain reputation.
- **Deliverability:** warm the sending domain, honor unsubscribes, never blast unverified lists. (This is why verified venue emails matter — see `target-venues-by-beach.md`.)

## Voice per pipeline

| Pipeline | Voice | Signed by |
|---|---|---|
| Sales (venues) | formal-warm business | Renata (secretary) |
| PR (journalists) | data-forward, concise | Renata or founder |
| Partnerships | friendly-peer, mutual | Renata |
| Influencers | casual, genuine fan | founder / first-person |

## What stays human
- The actual sales *calls* (Shimon — see `call-script-shimon.md`)
- Live influencer relationship management
- Any negotiation
- Payment / contracts
