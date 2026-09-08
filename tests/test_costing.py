from isurvive.catalog import load_catalog
from isurvive.costing import evaluate_kit, failures, min_price_cents
from isurvive.catalog import Kit


def test_min_price_is_ceil_landed_over_0_70():
    assert min_price_cents(70) == 100
    assert min_price_cents(0) == 0
    assert min_price_cents(54400) == 77715


def test_catalog_passes_margin_and_bom_sums():
    assert failures() == []
    catalog = load_catalog()
    assert catalog.costing_status == "estimate"
    assert catalog.kits
    for kit in catalog.kits:
        check = evaluate_kit(kit)
        assert check.ok, kit.sku
        assert check.bom_matches_landed
        assert kit.self_source_cents() <= kit.landed_cents
        assert kit.pack_list()


def test_photos_exist():
    catalog = load_catalog()
    from isurvive.catalog import ROOT

    for kit in catalog.kits:
        path = ROOT / kit.photo
        assert path.is_file(), kit.photo
        assert path.read_text(encoding="utf-8").lstrip().startswith("<svg")


def test_low_price_fails_margin():
    kit = Kit(
        sku="ISV-FAIL",
        name="bad",
        path="kit",
        summary="x",
        photo="kits/photos/ISV-FK-01.svg",
        landed_cents=1000,
        price_cents=1000,
        includes_skus=(),
        bom=(),
    )
    check = evaluate_kit(kit)
    assert not check.ok
    assert check.min_price_cents == 1429
