from __future__ import annotations

from pathlib import Path

from isurvive.catalog import ROOT

KNOWLEDGE_DIR = ROOT / "operator" / "knowledge"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta: dict[str, str] = {}
    for raw_line in parts[1].strip().splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, parts[2].strip()


def _split_list(value: str) -> list[str]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    return [item.strip().strip("'\"") for item in value.split(",") if item.strip()]


def load_modules(path: Path | None = None) -> list[dict]:
    directory = path or KNOWLEDGE_DIR
    modules = []
    for file in sorted(directory.glob("*.md")):
        meta, body = parse_frontmatter(file.read_text(encoding="utf-8"))
        modules.append(
            {
                "id": meta.get("id", file.stem),
                "title": meta.get("title", file.stem),
                "tags": _split_list(meta.get("tags", "")),
                "problems": _split_list(meta.get("problems", "")),
                "settings": _split_list(meta.get("settings", "")),
                "climates": _split_list(meta.get("climates", "")),
                "body": body,
                "path": str(file.relative_to(ROOT)).replace("\\", "/"),
            }
        )
    return modules


def score_module(module: dict, situation: dict) -> int:
    score = 0
    problems = set(situation.get("problems") or [])
    tags = set(module["tags"]) | set(module["problems"])
    score += 4 * len(problems & set(module["problems"]))
    score += 2 * len(problems & tags)
    setting = situation.get("setting")
    climate = situation.get("climate")
    if setting and setting in module["settings"]:
        score += 3
    if climate and climate in module["climates"]:
        score += 2
    gear = set(situation.get("gear") or [])
    if gear & tags:
        score += 1
    return score


def adapt(situation: dict, modules: list[dict] | None = None, limit: int = 4) -> dict:
    catalog = modules if modules is not None else load_modules()
    ranked = sorted(
        ((score_module(module, situation), module) for module in catalog),
        key=lambda item: (-item[0], item[1]["id"]),
    )
    selected = [module for score, module in ranked if score > 0][:limit]
    if not selected:
        selected = [module for _, module in ranked[: min(2, len(ranked))]]
    hours = int(situation.get("hours") or 24)
    people = max(1, int(situation.get("people") or 1))
    setting = situation.get("setting") or "unspecified"
    climate = situation.get("climate") or "mixed"
    briefing = [
        f"Situation lock: {people} person(s), ~{hours}h, {setting}, {climate}.",
        "This is kit-and-field guidance, not medical or emergency-services advice.",
    ]
    if hours <= 12:
        briefing.append("Window is short. Prioritize water, shelter, light, and a way out.")
    elif hours <= 72:
        briefing.append("Multi-day window. Ration power, filter water, keep the SBC dry.")
    else:
        briefing.append("Long stay. Repair beats replace. Inventory fasteners before you need them.")
    if people > 1:
        briefing.append(
            f"Split tasks across {people}: one on water/shelter, one on power/compute, rotate watch."
        )
    return {
        "disclaimer": (
            "Not medical, legal, or emergency-services advice. "
            "If someone is injured or you are in immediate danger, contact local emergency services. "
            "Do not put medical or personal data into this tree."
        ),
        "briefing": briefing,
        "modules": [
            {
                "id": module["id"],
                "title": module["title"],
                "path": module["path"],
                "body": _personalize(module["body"], situation),
            }
            for module in selected
        ],
    }


def _personalize(body: str, situation: dict) -> str:
    replacements = {
        "{{setting}}": situation.get("setting") or "your setting",
        "{{climate}}": situation.get("climate") or "current weather",
        "{{hours}}": str(situation.get("hours") or "the time you have"),
        "{{people}}": str(situation.get("people") or "1"),
    }
    for key, value in replacements.items():
        body = body.replace(key, value)
    return body
