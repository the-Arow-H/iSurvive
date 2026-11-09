"""Schema and safety checks for the offline North America field guide."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "scripts" / "build_guide.py"
    spec = importlib.util.spec_from_file_location("build_guide", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_guide_validates_and_builds():
    guide = _load()
    pages = guide.load_pages()
    guide.validate(pages)
    plants = [page for page in pages if page["kind"] == "plant"]
    assert len(plants) >= 15
    for plant in plants:
        assert plant["lookalikes"]
        assert "DEADLY LOOK-ALIKES" in plant["text"]
        assert "single identification" in plant["text"].lower()
    biomes = {page["id"] for page in pages if page["module"] == "biomes"}
    assert set(guide.BIOMES) <= biomes
    aid = [page for page in pages if page["module"] == "first-aid"]
    assert len(aid) >= 5
    assert all(page["review"] == "pending-clinical" for page in aid)
    for module, minimum in guide.MODULES_MIN_PAGES.items():
        assert sum(page["module"] == module for page in pages) >= minimum
    assert not any(guide.DOSE_RE.search(page["text"]) for page in pages)
    built = guide.build()
    assert (ROOT / "app" / "data" / "pages.json").exists()
    assert (ROOT / "app" / "sw.js").exists()
    sw = (ROOT / "app" / "sw.js").read_text(encoding="utf-8")
    assert "caches.match" in sw
    assert "/data/pages.json" in sw
    assert "/manifest.webmanifest" in sw
    assert len(built) == len(pages)


def test_no_external_runtime_assets():
    html = (ROOT / "app" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "app" / "js" / "guide.js").read_text(encoding="utf-8")
    css = (ROOT / "app" / "css" / "guide.css").read_text(encoding="utf-8")
    for text in (html, js, css):
        assert "google-analytics" not in text.lower()
        assert "googletagmanager" not in text.lower()
        assert not re.search(r"https?://", text)


def test_licenses_present():
    assert (ROOT / "LICENSE-CONTENT").exists()
    assert "CC BY-SA 4.0" in (ROOT / "LICENSE-CONTENT").read_text(encoding="utf-8")
    assert "MIT License" in (ROOT / "app" / "LICENSE").read_text(encoding="utf-8")
    assert (ROOT / "DISCLAIMER.md").exists()
    vendor = (ROOT / "app" / "vendor" / "MINISEARCH-LICENSE.txt").read_text(encoding="utf-8")
    assert "Luca Ongaro" in vendor
