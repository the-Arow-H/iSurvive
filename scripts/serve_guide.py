#!/usr/bin/env python3
"""Serve app/ with the manifest content type Lighthouse expects.

Usage: python3 scripts/serve_guide.py 4173
"""

from __future__ import annotations

import functools
import http.server
import mimetypes
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "app"
mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("application/javascript", ".js")


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4173
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"serving {ROOT} on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
