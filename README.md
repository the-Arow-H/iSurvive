# iSurvive

**Survival Knowledge for the problems you face, on device and interactive to your situation.**

Open field-kit + local-compute stack. Build in public on [@the_Arow_H](https://x.com/the_Arow_H).

**License:** [Apache-2.0](./LICENSE)  
**GitHub:** https://github.com/the-Arow-H/iSurvive  
**Origin:** TBD (dual-host — same SHA after every tag)

## What this is

Practical survival knowledge you can run **on your own device**, adapted to **your** situation — not a feed of generic tips. Kit BOM, dual compute (phone/SBC + local weights), repairable parts, community manual.

Asimov 1 is used as a **pattern** (kit *or* self-source, printed repairable modules, dual compute, own the stack) — **not** a humanoid promise.

## Build order (do not invert)

1. **Kit sales** — SKU, landed cost, photo, checkout, margin (`price ≥ landed / 0.70`)
2. **Dual host** — public git **and** Origin; same SHA after every tag
3. **Free GrokBot template** — Field Kit Operator (Apache-2.0)
4. **Build-in-public** — steward drafts on X; human hits publish

## Status

- Repo standing up 2026-09-06
- Local hub: Acer Desktop\workspace
- Ollama on Jarvis (smoke model live); Comfy install in progress
- Kit costing: catalog + margin gate live; Stripe checkout when `STRIPE_SECRET_KEY` is set
- Origin remote: open (add `origin-host` when the URL exists)

## Run the local hub

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
python -m isurvive margin
python -m isurvive serve
```

Open http://127.0.0.1:8080

- **Kits** — SKU, landed, photo, BOM, margin, checkout
- **Operator** — situation in → adapted modules out (optional Ollama rewrite)
- **Hub** — Ollama / Jarvis reachability and dual-host config

Point `OLLAMA_HOST` at Jarvis when the smoke model is the one you want. Leave Comfy off the field kit until that install is actually done.

## Kit sales

Source of truth: [`kits/catalog.json`](kits/catalog.json). Photos: [`kits/photos/`](kits/photos/). Rule is enforced in CI:

```text
price_cents >= ceil(landed_cents / 0.70)
```

Landed must equal the BOM sum. Self-source skips `kit-only` lines (QC, packing, outbound freight) and fabricates `P` (polymer print) / buys `X` (off-the-shelf).

Checkout is Stripe Checkout Sessions. No `payment_method_types`. Do not enable automatic tax until a registration exists.

## Dual host

GitHub is `origin`. Origin (second host) is TBD — add it as `origin-host` and then:

```bash
scripts/push-tag-dual-host.sh v0.1.0
python -m isurvive verify-host
```

Every tag must resolve to the **same SHA** on both remotes.

## Field Kit Operator (free GrokBot template)

[`operator/grokbot/FIELD_KIT_OPERATOR.md`](operator/grokbot/FIELD_KIT_OPERATOR.md) — Apache-2.0. Paste into a GrokBot. It drafts; it does not publish.

Knowledge modules live in [`operator/knowledge/`](operator/knowledge/).

## Build in public

Steward drafts: [`drafts/x/`](drafts/x/). Human hits publish on X. Do not put medical or personal data in drafts.

## Contributing

Issues and PRs welcome once the dual-remote mirror is live. Keep medical / personal data out of this tree. See [CONTRIBUTING.md](CONTRIBUTING.md).
