# Dual host

Build step 2. Public git (GitHub) **and** Origin. Same SHA after every tag.

Origin URL is **TBD**. Until it exists, `python -m isurvive verify-host` fails closed.

## Remotes

| Remote | Role |
| --- | --- |
| `origin` | GitHub `https://github.com/the-Arow-H/iSurvive` |
| `origin-host` | Origin (set when the URL is no longer TBD) |

```bash
git remote add origin-host <ORIGIN_URL>
export ORIGIN_REMOTE_URL=<ORIGIN_URL>
scripts/push-tag-dual-host.sh v0.1.0
python -m isurvive verify-host
```

The verify command `git ls-remote`s each tag on both remotes and requires identical SHAs. Do not move tags. If a tag must be corrected, cut a new tag.

Issues and PRs from outside contributors wait until this mirror is live (see root README).
