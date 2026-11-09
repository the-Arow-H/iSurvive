# Contributing

Keep personal data out of this tree. That includes health details of a real person, real names tied to a situation, phone numbers, and precise home addresses.

The North America field guide may include first-aid pages. They are not a free pass for treatment protocols:

- Every first-aid page carries `review: pending-clinical` until a licensed clinician records a last look.
- Every first-aid page says it is not medical advice.
- No drug doses. No milligram amounts.
- Claims cite a public source listed in `sources/SOURCES.md`.
- Operator modules in `operator/knowledge/` still do not grow treatment protocols.

## Build order

Do not invert: kit sales → dual host → Field Kit Operator template → build-in-public drafts.

## Checks before a PR

```bash
pip install -e ".[dev]"
python -m isurvive margin
pytest
```

A SKU cannot ship if `python -m isurvive margin` fails.

## Kit changes

1. Edit `kits/catalog.json` (SKU, landed cents, price cents, BOM, photo path).
2. Landed **must** equal the BOM sum.
3. Price **must** be `>= ceil(landed / 0.70)`.
4. Add or update `kits/photos/<SKU>.svg` (studio photo can replace the drawing later).
5. Do not enable Stripe Tax in checkout without an active registration.

## Operator knowledge

Modules in `operator/knowledge/` use a short frontmatter block (`id`, `title`, `tags`, `problems`, `settings`, `climates`). Write for a situation, not a generic tip list. No treatment protocols in that folder.

Field-guide pages in `content/na/` use the frontmatter checked by `scripts/build_guide.py`. Plant cards need a deadly-look-alike section and the single-identification rule. Run `python3 scripts/build_guide.py` after editing them.

## Dual host

Leave Origin as TBD until the second remote URL exists. After that, every tag is pushed to GitHub **and** `origin-host`, then verified with `python -m isurvive verify-host`.

## X

Put drafts in `drafts/x/`. Do not publish from a bot. The steward hits publish on [@the_Arow_H](https://x.com/the_Arow_H).
