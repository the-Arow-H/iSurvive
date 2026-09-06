import csv

from isurvive.catalog import ROOT, load_catalog


def test_bom_csv_covers_catalog():
    with (ROOT / "kits/BOM.csv").open(encoding="utf-8", newline="") as handle:
        keyed = {(row["sku"], row["pn"]) for row in csv.DictReader(handle)}
    for kit in load_catalog().kits:
        for line in kit.bom:
            assert (kit.sku, line.pn) in keyed, (kit.sku, line.pn)
