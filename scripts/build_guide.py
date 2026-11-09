#!/usr/bin/env python3
"""Build the offline North America field guide from content/na Markdown.

Stdlib only. Writes app/data/pages.json, app/sw.js, app/icons, and a
NOMAD content-pack manifest. The guide app does not fetch anything off
the device at runtime.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "na"
SOURCES = ROOT / "sources" / "SOURCES.md"
DISCLAIMER = ROOT / "DISCLAIMER.md"
APP = ROOT / "app"
MODULES_MIN_PAGES = {
    "shelter": 5,
    "water": 5,
    "first-aid": 5,
    "flora": 5,
    "fauna": 5,
}
BIOMES = [
    "eastern-deciduous",
    "boreal-taiga",
    "great-plains",
    "desert-southwest",
    "pacific-northwest",
    "rockies-alpine",
    "arctic-tundra",
    "gulf-southeast",
]
DOSE_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|milligrams)\b", re.I)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("missing frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("unclosed frontmatter")
    meta: dict = {}
    key = None
    for raw in parts[1].strip().splitlines():
        if not raw.strip():
            continue
        if raw.startswith("  - "):
            if key is None or not isinstance(meta.get(key), list):
                raise ValueError(f"list item without a key: {raw}")
            meta[key].append(raw[4:].strip().strip("'\""))
            continue
        if ":" not in raw:
            raise ValueError(f"bad frontmatter line: {raw}")
        k, v = raw.split(":", 1)
        key = k.strip()
        value = v.strip()
        if value == "":
            meta[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            meta[key] = (
                []
                if not inner
                else [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
            )
        else:
            meta[key] = value.strip("'\"")
    return meta, parts[2].strip() + "\n"


def _inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
        r'<a href="\2" rel="noopener noreferrer">\1</a>',
        escaped,
    )
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)
    return escaped


def render_markdown(body: str) -> str:
    lines = body.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("### "):
            out.append(f"<h3>{_inline(line[4:])}</h3>")
            i += 1
            continue
        if line.startswith("## "):
            out.append(f"<h2>{_inline(line[3:])}</h2>")
            i += 1
            continue
        if line.startswith("# "):
            out.append(f"<h2>{_inline(line[2:])}</h2>")
            i += 1
            continue
        if line.startswith("> "):
            quote = [line[2:]]
            i += 1
            while i < len(lines) and lines[i].startswith("> "):
                quote.append(lines[i][2:])
                i += 1
            out.append(f"<blockquote><p>{_inline(' '.join(quote))}</p></blockquote>")
            continue
        if re.match(r"^[-*] ", line):
            items = []
            while i < len(lines) and re.match(r"^[-*] ", lines[i]):
                items.append(f"<li>{_inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        if re.match(r"^\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(f"<li>{_inline(re.sub(r'^\\d+\\. ', '', lines[i]))}</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        para = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#{1,3} |> |[-*] |\d+\. )", lines[i]
        ):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{_inline(' '.join(para))}</p>")
    return "\n".join(out)


def load_source_ids(text: str | None = None) -> set[str]:
    raw = text if text is not None else SOURCES.read_text(encoding="utf-8")
    return set(re.findall(r"^## ([a-z0-9][a-z0-9-]*)\s*$", raw, re.M))


def iter_markdown() -> list[Path]:
    files = sorted(CONTENT.rglob("*.md"))
    if not files:
        raise SystemExit(f"no markdown under {CONTENT}")
    return files


def load_pages() -> list[dict]:
    source_ids = load_source_ids()
    pages = []
    seen = set()
    for path in iter_markdown():
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        rel = path.relative_to(CONTENT).as_posix()
        page_id = meta.get("id") or path.stem
        if page_id in seen:
            raise ValueError(f"duplicate id {page_id}")
        seen.add(page_id)
        module = meta.get("module")
        if not module:
            raise ValueError(f"{rel}: module is required")
        sources = meta.get("sources") or []
        if isinstance(sources, str):
            sources = [sources]
        if not sources:
            raise ValueError(f"{rel}: sources required")
        missing = [item for item in sources if item not in source_ids]
        if missing:
            raise ValueError(f"{rel}: unknown source ids {missing}")
        if not meta.get("title") or not meta.get("summary"):
            raise ValueError(f"{rel}: title and summary required")
        if not meta.get("last_reviewed"):
            raise ValueError(f"{rel}: last_reviewed required")
        if DOSE_RE.search(body):
            raise ValueError(f"{rel}: drug dose pattern is not allowed")
        if module == "first-aid" and meta.get("review") != "pending-clinical":
            raise ValueError(f"{rel}: first-aid pages need review: pending-clinical")
        if module == "flora" and meta.get("kind") == "plant":
            for field in ("name", "sci", "season", "lookalikes"):
                if not meta.get(field):
                    raise ValueError(f"{rel}: plant card missing {field}")
            if "DEADLY LOOK-ALIKES" not in body:
                raise ValueError(f"{rel}: plant card missing DEADLY LOOK-ALIKES")
            if "single identification" not in body.lower():
                raise ValueError(f"{rel}: plant card missing the single-identification rule")
        biomes = meta.get("biomes") or []
        if isinstance(biomes, str):
            biomes = [biomes]
        unknown = [b for b in biomes if b not in BIOMES]
        if unknown:
            raise ValueError(f"{rel}: unknown biomes {unknown}")
        plain = re.sub(r"\s+", " ", body).strip()
        pages.append(
            {
                "id": page_id,
                "title": meta["title"],
                "module": module,
                "kind": meta.get("kind") or "guide",
                "summary": meta["summary"],
                "biomes": biomes,
                "season": meta.get("season") or "",
                "name": meta.get("name") or "",
                "sci": meta.get("sci") or "",
                "usda_symbol": meta.get("usda_symbol") or "",
                "lookalikes": meta.get("lookalikes") or [],
                "sources": sources,
                "review": meta.get("review") or "none",
                "last_reviewed": meta["last_reviewed"],
                "path": f"content/na/{rel}",
                "html": render_markdown(body),
                "text": plain,
            }
        )
    return pages


def validate(pages: list[dict]) -> None:
    counts: dict[str, int] = {}
    plants = []
    biomes = []
    for page in pages:
        counts[page["module"]] = counts.get(page["module"], 0) + 1
        if page["module"] == "flora" and page["kind"] == "plant":
            plants.append(page)
        if page["module"] == "biomes":
            biomes.append(page["id"])
    for module, minimum in MODULES_MIN_PAGES.items():
        if counts.get(module, 0) < minimum:
            raise SystemExit(f"{module} has {counts.get(module, 0)} pages; need {minimum}")
    if len(plants) < 15:
        raise SystemExit(f"need 15 plant cards, found {len(plants)}")
    missing_biomes = [b for b in BIOMES if b not in biomes]
    if missing_biomes:
        raise SystemExit(f"missing biome stubs: {missing_biomes}")
    aid = [p for p in pages if p["module"] == "first-aid"]
    if any(p["review"] != "pending-clinical" for p in aid):
        raise SystemExit("a first-aid page is missing pending-clinical")
    if not aid:
        raise SystemExit("no first-aid pages")


def _png(size: int, draw) -> bytes:
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            raw.extend(draw(x, y))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")


def _icon(size: int) -> bytes:
    def draw(x: int, y: int) -> tuple[int, int, int]:
        cx = cy = (size - 1) / 2
        nx = (x - cx) / (size / 2)
        ny = (y - cy) / (size / 2)
        # cream field, ink ring, a simple ridge line
        if nx * nx + ny * ny > 0.90:
            return (28, 36, 28)
        if abs(ny - (-0.15 + 0.22 * nx * nx)) < 0.035 and ny < 0.05:
            return (242, 236, 220)
        if 0.42 < ny < 0.78 and abs(nx) < 0.08:
            return (47, 90, 58)
        if ny > 0.55:
            return (232, 224, 204)
        return (36, 64, 46)

    return _png(size, draw)


def precache_files() -> list[str]:
    rels = []
    for path in sorted(APP.rglob("*")):
        if not path.is_file():
            continue
        if path.name == "sw.js":
            continue
        if path.suffix in {".map"}:
            continue
        rel = "/" + path.relative_to(APP).as_posix()
        rels.append(rel)
    if "/index.html" not in rels:
        raise SystemExit("app/index.html missing")
    return rels


def write_service_worker(files: list[str]) -> None:
    digest = hashlib.sha256("\n".join(files).encode()).hexdigest()[:12]
    payload = json.dumps(files, indent=2)
    script = f"""/* iSurvive field guide service worker. Cache-first. Generated. */
const CACHE = "isurvive-guide-{digest}";
const PRECACHE = {payload};

self.addEventListener("install", (event) => {{
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)));
  self.skipWaiting();
}});

self.addEventListener("activate", (event) => {{
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))
    ).then(() => self.clients.claim())
  );
}});

self.addEventListener("fetch", (event) => {{
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) {{
    return;
  }}
  event.respondWith(
    caches.match(event.request).then((cached) => {{
      if (cached) return cached;
      return fetch(event.request)
        .then((response) => {{
          if (response && response.ok && event.request.method === "GET") {{
            const copy = response.clone();
            caches.open(CACHE).then((cache) => cache.put(event.request, copy));
          }}
          return response;
        }})
        .catch(() => caches.match("/index.html"));
    }})
  );
}});
"""
    (APP / "sw.js").write_text(script, encoding="utf-8")


def write_nomad(pages: list[dict]) -> None:
    pack = {
        "name": "isurvive-na",
        "version": "0.1.0",
        "title": "iSurvive North America field guide",
        "license_content": "CC BY-SA 4.0",
        "license_code": "MIT",
        "pages": [
            {"id": p["id"], "module": p["module"], "title": p["title"], "path": p["path"]}
            for p in pages
        ],
    }
    out = ROOT / "build" / "nomad"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack.json").write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    (ROOT / "build" / "zim").mkdir(parents=True, exist_ok=True)


def build() -> list[dict]:
    pages = load_pages()
    validate(pages)
    data = {
        "name": "iSurvive NA",
        "version": "0.1.0",
        "built_from": "content/na",
        "pages": pages,
    }
    blob = json.dumps(data, ensure_ascii=False, indent=2)
    (APP / "data").mkdir(parents=True, exist_ok=True)
    (APP / "data" / "pages.json").write_text(blob + "\n", encoding="utf-8")
    icons = APP / "icons"
    icons.mkdir(parents=True, exist_ok=True)
    (icons / "icon-192.png").write_bytes(_icon(192))
    (icons / "icon-512.png").write_bytes(_icon(512))
    write_nomad(pages)
    write_service_worker(precache_files())
    return pages


def main() -> None:
    pages = build()
    counts: dict[str, int] = {}
    for page in pages:
        counts[page["module"]] = counts.get(page["module"], 0) + 1
    plants = sum(1 for p in pages if p["kind"] == "plant")
    print(f"pages={len(pages)} plants={plants} modules={counts}")


if __name__ == "__main__":
    main()
