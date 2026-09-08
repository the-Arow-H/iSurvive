# Kit sales

Build step 1. A kit is not for sale until all five exist: **SKU**, **landed cost**, **photo**, **checkout**, **margin**.

## Rule

```text
price >= landed / 0.70
```

Implemented as integer cents:

```text
min_price_cents = ceil(landed_cents / 0.70)
price_cents >= min_price_cents
landed_cents == sum(qty * unit_landed_cents)
```

That is a 30% gross-margin floor on landed. It is not a promise about net after ads, returns, or failed boards.

## Files

| Piece | Where |
| --- | --- |
| Catalog | `kits/catalog.json` |
| Costing worksheet | `kits/COSTING.md` |
| Photos | `kits/photos/<SKU>.svg` |
| Costing | `isurvive/costing.py` |
| Checkout | `isurvive/checkout.py` → `POST /api/checkout` |
| Webhook | `POST /api/stripe/webhook` |

## Process codes

| Code | Meaning |
| --- | --- |
| `P` | Polymer print (repairable module) |
| `X` | Off-the-shelf |

Self-source: drop `kit-only` lines (QC, packing, outbound freight). `self_source_cents` is that sum.

Checkout is Stripe Checkout Sessions. `POST /api/stripe/webhook` handles `checkout.session.completed`. No `payment_method_types`. No `automatic_tax` until a registration is active.

A live charge waits on `costing_status: quoted` plus `STRIPE_SECRET_KEY`. Estimates ship in the catalog; they do not take cards by themselves.
