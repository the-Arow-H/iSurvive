from fastapi.testclient import TestClient

from isurvive.checkout import CheckoutError, create_checkout_session
from isurvive.catalog import load_catalog
from isurvive.costing import evaluate_kit
from isurvive.hub import create_app


def test_health_and_kits():
    client = TestClient(create_app())
    health = client.get("/api/health")
    assert health.status_code == 200
    kits = client.get("/api/kits")
    assert kits.status_code == 200
    body = kits.json()
    assert body["price_rule"].startswith("price >=")
    assert len(body["kits"]) >= 6
    assert body["kits"][0]["sku"].startswith("ISV-")
    page = client.get("/")
    assert page.status_code == 200
    assert b"iSurvive" in page.content


def test_operator_endpoint():
    client = TestClient(create_app())
    res = client.post(
        "/api/operator",
        json={
            "setting": "urban",
            "climate": "wet",
            "hours": 36,
            "people": 3,
            "problems": ["shelter", "power"],
            "gear": ["ISV-FK-01"],
            "notes": "do not store this",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["modules"]
    assert data["local_rewrite"] is None
    joined = " ".join(m["id"] for m in data["modules"])
    assert "shelter" in joined or "power-compute" in joined


def test_checkout_requires_key_and_margin(monkeypatch):
    kit = load_catalog().by_sku("ISV-FK-01")
    assert evaluate_kit(kit).ok
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    try:
        create_checkout_session(
            kit,
            quantity=1,
            success_url="http://x/ok",
            cancel_url="http://x/no",
        )
        raise AssertionError("should require stripe key")
    except CheckoutError as exc:
        assert "STRIPE_SECRET_KEY" in str(exc)

    client = TestClient(create_app())
    res = client.post("/api/checkout", json={"sku": "ISV-FK-01", "quantity": 1})
    assert res.status_code == 400


def test_grokbot_template_present():
    from isurvive.catalog import ROOT

    text = (ROOT / "operator/grokbot/FIELD_KIT_OPERATOR.md").read_text(encoding="utf-8")
    assert "Never publish to X" in text
    assert "price >= landed / 0.70" in text
