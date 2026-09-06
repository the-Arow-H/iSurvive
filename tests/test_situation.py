from isurvive.situation import adapt, load_modules, parse_frontmatter, score_module


def test_frontmatter_and_modules():
    meta, body = parse_frontmatter("---\nid: x\ntags: [a, b]\n---\nHello")
    assert meta["id"] == "x"
    assert "Hello" in body
    modules = load_modules()
    ids = {m["id"] for m in modules}
    assert {"water", "shelter", "power-compute", "repair", "navigation", "kit-assembly"} <= ids


def test_water_problem_ranks_water_module():
    modules = load_modules()
    situation = {
        "setting": "desert",
        "climate": "hot",
        "hours": 8,
        "people": 2,
        "problems": ["water"],
        "gear": ["ISV-WT-01"],
    }
    water = next(m for m in modules if m["id"] == "water")
    nav = next(m for m in modules if m["id"] == "navigation")
    assert score_module(water, situation) > score_module(nav, situation)
    out = adapt(situation, modules)
    assert out["modules"][0]["id"] == "water"
    assert "2 person" in out["briefing"][0]
    assert "desert" in out["modules"][0]["body"]
    assert "medical" in out["disclaimer"].lower()
