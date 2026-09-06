#!/usr/bin/env bash
set -euo pipefail
# Push the current branch and a tag to GitHub and Origin.
# Origin remote name: origin-host (URL still TBD).
TAG="${1:-}"
if [[ -z "$TAG" ]]; then
  echo "usage: $0 <tag>" >&2
  exit 2
fi
git tag -a "$TAG" -m "iSurvive $TAG"
git push origin "$TAG"
if git remote get-url origin-host >/dev/null 2>&1; then
  git push origin-host "$TAG"
  python -m isurvive verify-host
else
  echo "origin-host remote is TBD — tag pushed to GitHub only"
  exit 1
fi
