# Buildout (do not invert)

Work this list in order. Do not skip kit sales for operator polish. Do not skip dual-host for X drafts.

## 1. Kit sales

A SKU cannot ship without **SKU · landed · photo · checkout · margin**.

- [x] Catalog with SKUs, landed cents, BOM sum, photos, `price >= landed / 0.70`
- [x] Stripe Checkout Sessions (no `payment_method_types`, no tax until a registration)
- [x] Margin gate in CLI + CI
- [ ] Costing worksheet: estimate vs quote, as-of date, vendor class *(this pass: metadata + `kits/COSTING.md`)*
- [ ] Self-source path: drop `kit-only` lines, show self-source landed *(this pass)*
- [ ] Pack / QC list per SKU *(this pass)*
- [ ] Checkout webhook `checkout.session.completed` *(this pass)*
- [ ] Checkout success shows packing list *(this pass)*
- [ ] `STRIPE_SECRET_KEY` on the selling host (human)
- [ ] Studio photos replace catalog drawings (human)
- [ ] Quoted landed costs replace steward estimates before live charge (human)
- [ ] Stripe Tax only after an active registration (do not enable now)

## 2. Dual host

Public git **and** Origin. Same SHA after every tag.

- [x] GitHub `the-Arow-H/iSurvive`
- [x] Origin `unlimitedpracticeguide/iSurvive` (default branch `main`)
- [ ] Remotes in this clone: `github` = GitHub, `origin` = Origin *(this pass: detect + verify)*
- [ ] `python -m isurvive verify-host` against live remotes *(this pass)*
- [ ] Tag push script writes **both** remotes *(this pass)*
- [ ] First release tag after this tooling is green (human hits tag)
- [ ] CI cannot see Origin without a secret — keep verify-host local

## 3. Field Kit Operator (free GrokBot)

- [x] Apache-2.0 template `operator/grokbot/FIELD_KIT_OPERATOR.md`
- [x] Situation retriever + hub `POST /api/operator`
- [ ] Community manual in the hub *(this pass)*
- [ ] Knowledge: comms, food, weather, signaling; emergency-services pointer only *(this pass)*
- [ ] Gear picker from catalog SKUs *(this pass)*
- [ ] Template updated for live Origin remotes *(this pass)*
- [ ] Paste template into a GrokBot (human)
- [ ] Ollama on Jarvis for optional rewrite (already the path; leave Comfy on the desk)

## 4. Build in public

- [x] Drafts live in `drafts/x/`; bot does not publish
- [ ] Draft: Origin mirror live *(this pass)*
- [ ] Draft: kit catalog + margin rule *(this pass)*
- [ ] Human publishes on [@the_Arow_H](https://x.com/the_Arow_H)

## Later (after 1–4)

- Printed-part fabrication notes (`docs/fabrication.md`)
- Phone PWA / offline cache of the operator
- Quoted vendor SKUs and real inbound freight
- Shipping beyond US/CA once landed is known
