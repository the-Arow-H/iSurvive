from isurvive.dual_host import verify_tags


def test_origin_tbd_is_not_ok(monkeypatch):
    monkeypatch.delenv("ORIGIN_REMOTE_URL", raising=False)
    monkeypatch.setenv("ORIGIN_REMOTE_NAME", "origin-host-missing")
    result = verify_tags()
    assert result["ok"] is False
    assert "TBD" in result["reason"] or "origin-host" in result["reason"]
