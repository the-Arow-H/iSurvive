from __future__ import annotations

import os
import subprocess
from pathlib import Path

from isurvive.catalog import ROOT

GITHUB_REMOTE = os.environ.get("GITHUB_REMOTE_NAME", "origin")
ORIGIN_REMOTE = os.environ.get("ORIGIN_REMOTE_NAME", "origin-host")


def _git(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd or ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def remotes() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for line in _git("remote", "-v").splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] not in mapping:
            mapping[parts[0]] = parts[1]
    configured = os.environ.get("ORIGIN_REMOTE_URL", "").strip()
    if configured and ORIGIN_REMOTE not in mapping:
        mapping[ORIGIN_REMOTE] = configured
    return mapping


def tag_sha_on_remote(remote: str, tag: str) -> str | None:
    try:
        _git("fetch", remote, "refs/tags/*:refs/tags/verify-*", "--no-tags")
    except subprocess.CalledProcessError:
        pass
    output = subprocess.run(
        ["git", "ls-remote", remote, f"refs/tags/{tag}"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if output.returncode != 0 or not output.stdout.strip():
        return None
    return output.stdout.split()[0]


def local_tags() -> list[str]:
    if not _git("tag"):
        return []
    return [line for line in _git("tag").splitlines() if line]


def verify_tags(tags: list[str] | None = None) -> dict:
    names = remotes()
    github = names.get(GITHUB_REMOTE) or os.environ.get("GITHUB_REMOTE_URL", "")
    origin = names.get(ORIGIN_REMOTE) or os.environ.get("ORIGIN_REMOTE_URL", "")
    if not origin:
        return {
            "ok": False,
            "reason": "Origin remote is TBD. Set ORIGIN_REMOTE_URL or add remote origin-host.",
            "github": github,
            "origin": origin,
            "tags": [],
        }
    check = tags if tags is not None else local_tags()
    rows = []
    ok = True
    for tag in check:
        github_sha = tag_sha_on_remote(GITHUB_REMOTE, tag) if github else None
        origin_sha = tag_sha_on_remote(ORIGIN_REMOTE, tag) if origin else None
        match = bool(github_sha and origin_sha and github_sha == origin_sha)
        ok = ok and match
        rows.append(
            {
                "tag": tag,
                "github_sha": github_sha,
                "origin_sha": origin_sha,
                "match": match,
            }
        )
    if not check:
        return {
            "ok": False,
            "reason": "No tags to compare yet. After every tag, push both remotes and re-run.",
            "github": github,
            "origin": origin,
            "tags": [],
        }
    return {"ok": ok, "github": github, "origin": origin, "tags": rows}


def push_tag_both(tag: str) -> dict:
    names = remotes()
    if ORIGIN_REMOTE not in names and not os.environ.get("ORIGIN_REMOTE_URL"):
        raise RuntimeError("Origin remote is TBD — add origin-host before tagging for dual-host")
    _git("push", GITHUB_REMOTE, tag)
    origin = ORIGIN_REMOTE if ORIGIN_REMOTE in names else os.environ["ORIGIN_REMOTE_URL"]
    _git("push", origin, tag)
    return verify_tags([tag])
