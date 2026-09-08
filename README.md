# iSurvive

**Survival Knowledge for the problems you face, on device and interactive to your situation.**

Open field-kit + local-compute stack. Build in public on [@the_Arow_H](https://x.com/the_Arow_H).

**License:** [Apache-2.0](./LICENSE)  
**GitHub:** https://github.com/the-Arow-H/iSurvive  
**Origin:** https://origin.cursor.com/unlimitedpracticeguide/iSurvive (dual-host — same SHA after every tag)

## What this is

Practical survival knowledge you can run **on your own device**, adapted to **your** situation — not a feed of generic tips. Kit BOM, dual compute (phone/SBC + local weights), repairable parts, community manual.

Asimov 1 is used as a **pattern** (kit *or* self-source, printed repairable modules, dual compute, own the stack) — **not** a humanoid promise.

## Build order (do not invert)

1. **Kit sales** — SKU, landed cost, photo, checkout, margin (`price ≥ landed / 0.70`)
2. **Dual host** — public git **and** Origin; same SHA after every tag
3. **Free GrokBot template** — Field Kit Operator (Apache-2.0)
4. **Build-in-public** — steward drafts on X; human hits publish

The working list is [`docs/buildout.md`](docs/buildout.md).

## Status

- Dual host live: GitHub + Origin (default branch `main`)
- Kit catalog + margin gate live; costing is **estimate** until quoted
- Stripe checkout when `STRIPE_SECRET_KEY` is set; webhook at `POST /api/stripe/webhook`
- Local hub: Acer Desktop\workspace
- Ollama on Jarvis (smoke model live); Comfy install in progress

## Run the local hub

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
python -m isurvive margin
python -m isurvive verify-host
python -m isurvive serve
```

Open http://127.0.0.1:8080

## Kit sales

Source of truth: [`kits/catalog.json`](kits/catalog.json). Worksheet: [`kits/COSTING.md`](kits/COSTING.md). Photos: [`kits/photos/`](kits/photos/).

```text
price_cents >= ceil(landed_cents / 0.70)
```

Self-source skips `kit-only` lines. Do not take a live card while `costing_status` is `estimate`.

## Dual host

| Remote | URL |
| --- | --- |
| `github` | https://github.com/the-Arow-H/iSurvive |
| `origin` | https://origin.cursor.com/unlimitedpracticeguide/iSurvive |

```bash
scripts/push-branch-dual-host.sh
scripts/push-tag-dual-host.sh v0.1.0
python -m isurvive verify-host
```

## Field Kit Operator (free GrokBot template)

[`operator/grokbot/FIELD_KIT_OPERATOR.md`](operator/grokbot/FIELD_KIT_OPERATOR.md) — Apache-2.0. Paste into a GrokBot. It drafts; it does not publish.

## Build in public

Steward drafts: [`drafts/x/`](drafts/x/). Human hits publish on X.

## Contributing

Issues and PRs welcome. Keep medical / personal data out of this tree. See [CONTRIBUTING.md](CONTRIBUTING.md).
