#!/usr/bin/env bash
set -euo pipefail
python -m isurvive margin
python -m isurvive verify-host || true
