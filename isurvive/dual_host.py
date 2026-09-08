from __future__ import annotations

import os
import subprocess
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from isurvive.catalog import ROOT

GITHUB_MARKERS = ("github.com",)
ORIGIN_MARKERS = ("origin.cursor.com",)


def scrub_url(url: str) -> str:
    parsed = urlsplit(url)
    host = parsed.hostname or ""
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return urlunsplit((parsed.scheme, host, parsed.path, parsed.query, parsed.fragment))


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
    origin_name = os.environ.get("ORIGIN_REMOTE_NAME", "").strip()
    if configured and origin_name and origin_name not in mapping:
        mapping[origin_name] = configured
    return mapping


def _name_for(mapping: dict[str, str], env_key: str, markers: tuple[str, ...], fallback: str) -> str:
    forced = os.environ.get(env_key, "").strip()
    if forced:
        return forced
    for name, url in mapping.items():
        if any(marker in url for marker in markers):
            return name
    return fallback


def github_remote_name(mapping: dict[str, str] | None = None) -> str:
    return _name_for(mapping or remotes(), "GITHUB_REMOTE_NAME", GITHUB_MARKERS, "github")


def origin_remote_name(mapping: dict[str, str] | None = None) -> str:
    return _name_for(mapping or remotes(), "ORIGIN_REMOTE_NAME", ORIGIN_MARKERS, "origin")


def public_remotes() -> dict[str, str]:
    return {name: scrub_url(url) for name, url in remotes().items()}


def tag_sha_on_remote(remote: str, tag: str) -> str | None:
    output = subprocess.run(
        ["git", "ls-remote", remote, f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if output.returncode != 0 or not output.stdout.strip():
        return None
    for line in output.stdout.splitlines():
        sha, ref = line.split()
        if ref.endswith("^{}"):
            return sha
    return output.stdout.split()[0]


def head_sha_on_remote(remote: str, branch: str) -> str | None:
    output = subprocess.run(
        ["git", "ls-remote", remote, f"refs/heads/{branch}"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if output.returncode != 0 or not output.stdout.strip():
        return None
    return output.stdout.split()[0]


def local_tags() -> list[str]:
    try:
        text = _git("tag")
    except subprocess.CalledProcessError:
        return []
    if not text:
        return []
    return [line for line in text.splitlines() if line]


def current_branch() -> str:
    try:
        return _git("rev-parse", "--abbrev-ref", "HEAD")
    except subprocess.CalledProcessError:
        return "HEAD"


def verify_tags(tags: list[str] | None = None) -> dict:
    names = remotes()
    github_name = github_remote_name(names)
    origin_name = origin_remote_name(names)
    github = names.get(github_name) or os.environ.get("GITHUB_REMOTE_URL", "")
    origin = names.get(origin_name) or os.environ.get("ORIGIN_REMOTE_URL", "")
    public = {
        "github": scrub_url(github) if github else "",
        "origin": scrub_url(origin) if origin else "",
        "github_remote": github_name,
        "origin_remote": origin_name,
    }
    origin_ok = bool(origin) and any(marker in origin for marker in ORIGIN_MARKERS)
    github_ok = bool(github) and any(marker in github for marker in GITHUB_MARKERS)

    branch = current_branch()
    heads = [
        {
            "branch": branch,
            "github_sha": head_sha_on_remote(github_name, branch) if github_ok else None,
            "origin_sha": head_sha_on_remote(origin_name, branch) if origin_ok else None,
        }
    ]
    heads[0]["match"] = bool(
        heads[0]["github_sha"]
        and heads[0]["origin_sha"]
        and heads[0]["github_sha"] == heads[0]["origin_sha"]
    )

    if not github_ok or not origin_ok:
        return {
            "ok": False,
            "reason": "Origin remote is TBD. Set ORIGIN_REMOTE_URL or add an origin.cursor.com remote."
            if not origin_ok
            else "GitHub remote missing.",
            **public,
            "tags": [],
            "heads": heads,
        }

    check = tags if tags is not None else local_tags()
    rows = []
    tags_ok = True
    for tag in check:
        github_sha = tag_sha_on_remote(github_name, tag)
        origin_sha = tag_sha_on_remote(origin_name, tag)
        match = bool(github_sha and origin_sha and github_sha == origin_sha)
        tags_ok = tags_ok and match
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
            "ok": True,
            "reason": "Both remotes configured; no tags yet. After every tag, push github and origin.",
            **public,
            "tags": [],
            "heads": heads,
        }
    return {
        "ok": tags_ok,
        **public,
        "tags": rows,
        "heads": heads,
    }


def push_tag_both(tag: str) -> dict:
    names = remotes()
    github_name = github_remote_name(names)
    origin_name = origin_remote_name(names)
    if origin_name not in names and not os.environ.get("ORIGIN_REMOTE_URL"):
        raise RuntimeError("Origin remote missing — add origin.cursor.com before tagging")
    _git("push", github_name, tag)
    origin = origin_name if origin_name in names else os.environ["ORIGIN_REMOTE_URL"]
    _git("push", origin, tag)
    return verify_tags([tag])
