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
| Photos | `kits/photos/<SKU>.svg` |
| Costing | `isurvive/costing.py` |
| Checkout | `isurvive/checkout.py` → `POST /api/checkout` |

## Process codes

| Code | Meaning |
| --- | --- |
| `P` | Polymer print (repairable module) |
| `X` | Off-the-shelf |

`source: kit-only` lines (QC, packing, outbound freight) are not bought on the self-source path.

## Checkout

Stripe Checkout Sessions, hosted. Requires `STRIPE_SECRET_KEY`. Shipping address collected for US/CA until more countries are priced. No `payment_method_types` (dynamic methods). No `automatic_tax` until a registration is active.

The Field Kit Operator template refuses to sell a SKU that fails `python -m isurvive margin`.
