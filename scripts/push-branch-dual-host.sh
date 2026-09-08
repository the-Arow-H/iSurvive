#!/usr/bin/env bash
set -euo pipefail
# Push the current branch to GitHub and Origin without renaming it.
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
github_remote=github
origin_remote=origin
if git remote get-url github >/dev/null 2>&1; then
  github_remote=github
elif git remote get-url origin >/dev/null 2>&1 && git remote get-url origin | grep -q github.com; then
  github_remote=origin
fi
if git remote get-url origin >/dev/null 2>&1 && git remote get-url origin | grep -q origin.cursor.com; then
  origin_remote=origin
elif git remote get-url origin-host >/dev/null 2>&1; then
  origin_remote=origin-host
fi
git push -u "$github_remote" "HEAD:${BRANCH}"
git push -u "$origin_remote" "HEAD:${BRANCH}"
python -m isurvive verify-host
