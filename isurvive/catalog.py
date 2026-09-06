from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "kits" / "catalog.json"


@dataclass(frozen=True)
class BomLine:
    pn: str
    name: str
    qty: int
    unit_landed_cents: int
    process: str
    source: str

    @property
    def ext_landed_cents(self) -> int:
        return self.qty * self.unit_landed_cents


@dataclass(frozen=True)
class Kit:
    sku: str
    name: str
    path: str
    summary: str
    photo: str
    landed_cents: int
    price_cents: int
    includes_skus: tuple[str, ...]
    bom: tuple[BomLine, ...]

    def bom_sum_cents(self) -> int:
        return sum(line.ext_landed_cents for line in self.bom)

    def public_dict(self) -> dict[str, Any]:
        from isurvive.costing import evaluate_kit

        check = evaluate_kit(self)
        return {
            "sku": self.sku,
            "name": self.name,
            "path": self.path,
            "summary": self.summary,
            "photo": "/" + self.photo.replace("\\", "/"),
            "landed_cents": self.landed_cents,
            "price_cents": self.price_cents,
            "currency": "USD",
            "includes_skus": list(self.includes_skus),
            "margin_ok": check.ok,
            "min_price_cents": check.min_price_cents,
            "gross_margin": check.gross_margin,
            "bom": [
                {
                    "pn": line.pn,
                    "name": line.name,
                    "qty": line.qty,
                    "unit_landed_cents": line.unit_landed_cents,
                    "ext_landed_cents": line.ext_landed_cents,
                    "process": line.process,
                    "source": line.source,
                }
                for line in self.bom
            ],
        }


@dataclass(frozen=True)
class Catalog:
    currency: str
    margin_floor: float
    price_rule: str
    notes: str
    kits: tuple[Kit, ...]

    def by_sku(self, sku: str) -> Kit:
        for kit in self.kits:
            if kit.sku == sku:
                return kit
        raise KeyError(sku)


def _kit_from_raw(raw: dict[str, Any]) -> Kit:
    return Kit(
        sku=raw["sku"],
        name=raw["name"],
        path=raw["path"],
        summary=raw["summary"],
        photo=raw["photo"],
        landed_cents=int(raw["landed_cents"]),
        price_cents=int(raw["price_cents"]),
        includes_skus=tuple(raw.get("includes_skus") or ()),
        bom=tuple(
            BomLine(
                pn=line["pn"],
                name=line["name"],
                qty=int(line["qty"]),
                unit_landed_cents=int(line["unit_landed_cents"]),
                process=line.get("process", "X"),
                source=line.get("source", "kit-or-self"),
            )
            for line in raw.get("bom") or []
        ),
    )


def load_catalog(path: Path | None = None) -> Catalog:
    data = json.loads((path or CATALOG_PATH).read_text(encoding="utf-8"))
    kits = tuple(_kit_from_raw(item) for item in data["kits"])
    return Catalog(
        currency=data.get("currency", "USD"),
        margin_floor=float(data.get("margin_floor", 0.3)),
        price_rule=data.get("price_rule", "price >= landed / 0.70"),
        notes=data.get("notes", ""),
        kits=kits,
    )


@lru_cache(maxsize=1)
def catalog() -> Catalog:
    return load_catalog()
