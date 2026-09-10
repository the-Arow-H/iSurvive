# Dual host

Build step 2. Public git (GitHub) **and** Origin. Same SHA after every tag.

Origin is live: https://origin.cursor.com/unlimitedpracticeguide/iSurvive

## Remotes (this clone)

| Remote | Role |
| --- | --- |
| `github` | https://github.com/the-Arow-H/iSurvive |
| `origin` | https://origin.cursor.com/unlimitedpracticeguide/iSurvive |

Older clones that still have GitHub as `origin` should rename it to `github` and add Origin as `origin`. `isurvive.dual_host` detects hosts by URL (`github.com` vs `origin.cursor.com`).

```bash
scripts/push-branch-dual-host.sh
scripts/push-tag-dual-host.sh v0.1.0
python -m isurvive verify-host
```

`verify-host` `git ls-remote`s tags on both remotes and requires identical SHAs. It also reports whether the current branch heads match. Do not move tags. If a tag must be corrected, cut a new tag.

URLs printed by the hub are scrubbed of embedded credentials.
