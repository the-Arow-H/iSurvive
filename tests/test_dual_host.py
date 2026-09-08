from isurvive.dual_host import scrub_url, verify_tags


def test_origin_tbd_is_not_ok(monkeypatch):
    monkeypatch.delenv("ORIGIN_REMOTE_URL", raising=False)
    monkeypatch.setenv("ORIGIN_REMOTE_NAME", "origin-host-missing")
    result = verify_tags()
    assert result["ok"] is False
    assert "TBD" in result["reason"] or "origin.cursor.com" in result["reason"]


def test_scrub_url_drops_userinfo():
    assert (
        scrub_url("https://x-access-token:secret@github.com/the-Arow-H/iSurvive")
        == "https://github.com/the-Arow-H/iSurvive"
    )
