# Kit costing worksheet

Landed costs in `kits/catalog.json` are **steward estimates** until a quote is pasted here.
Do not take a live card until `costing_status` is `quoted` and `python -m isurvive margin` is green.

## Rule

```text
price_cents >= ceil(landed_cents / 0.70)
landed_cents == BOM sum
```

Self-source landed = sum of lines with `source != kit-only`.

## As of 2026-09-07

| SKU | Status | Kit landed | Self-source landed | Price | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| ISV-FK-01 | estimate | $544.00 | $495.00 | $799.00 | Includes nested modules + case + kitting |
| ISV-CM-01 | estimate | $163.00 | $154.00 | $249.00 | Pi-class 8GB; confirm board revision |
| ISV-PM-01 | estimate | $124.00 | $117.00 | $189.00 | 65W PD + 40W fold |
| ISV-WT-01 | estimate | $52.00 | $48.00 | $79.00 | Hollow-fiber; tabs are backup |
| ISV-SH-01 | estimate | $55.00 | $51.00 | $85.00 | Bivy is not a four-season tent |
| ISV-RP-01 | estimate | $48.00 | $44.00 | $75.00 | Print spares before the tray cracks |

Freight shares are reserves, not carrier invoices. Replace them with the last actual inbound/outbound before a live SKU.

## Vendor class (fill when quoting)

| PN | Class | Vendor | Quote date | Quote |
| --- | --- | --- | --- | --- |
| RPI5-8G | X | | | |
| NVME-128 | X | | | |
| PD-20K | X | | | |
| SOL-40W | X | | | |
| HF-FILTER | X | | | |
| BIVY | X | | | |
| CM-TRAY / PM-BAY / WT-MOUNT / SH-POUCH / SPARES | P | print farm or local | | |

Process: `P` polymer print, `X` off-the-shelf.
