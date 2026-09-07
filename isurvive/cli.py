from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from isurvive.catalog import ROOT, catalog
from isurvive.costing import evaluate_catalog
from isurvive.dual_host import verify_tags


def _cmd_margin(_args: argparse.Namespace) -> int:
    rows = evaluate_catalog()
    bad = [row for row in rows if not row.ok]
    for row in rows:
        mark = "OK" if row.ok else "FAIL"
        print(
            f"{row.sku:12} {mark:4} landed={row.landed_cents:6} "
            f"price={row.price_cents:6} min={row.min_price_cents:6} "
            f"bom={row.bom_sum_cents:6} margin={row.gross_margin:.1%}"
        )
    if bad:
        print(f"{len(bad)} SKU(s) fail price >= landed / 0.70 or BOM mismatch", file=sys.stderr)
        return 1
    print(f"{len(rows)} SKU(s) pass margin floor")
    return 0


def _cmd_catalog(_args: argparse.Namespace) -> int:
    cat = catalog()
    payload = {
        "currency": cat.currency,
        "price_rule": cat.price_rule,
        "kits": [kit.public_dict() for kit in cat.kits],
    }
    json.dump(payload, sys.stdout, indent=2)
    print()
    return 0


def _cmd_verify(_args: argparse.Namespace) -> int:
    result = verify_tags()
    json.dump(result, sys.stdout, indent=2)
    print()
    return 0 if result.get("ok") else 1


def _cmd_serve(args: argparse.Namespace) -> int:
    os.chdir(ROOT)
    host = args.host or os.environ.get("HOST", "127.0.0.1")
    port = int(args.port or os.environ.get("PORT", "8080"))
    try:
        from isurvive.hub import run_hub

        run_hub(host=host, port=port)
        return 0
    except ImportError:
        web = ROOT / "web"
        handler = SimpleHTTPRequestHandler
        os.chdir(web)
        server = ThreadingHTTPServer((host, port), handler)
        print(f"static fallback http://{host}:{port}")
        server.serve_forever()
        return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="isurvive")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("margin", help="enforce price >= landed / 0.70")
    sub.add_parser("catalog", help="print public kit catalog JSON")
    sub.add_parser("verify-host", help="require GitHub and Origin tag SHAs to match")

    serve = sub.add_parser("serve", help="run the local hub")
    serve.add_argument("--host", default=None)
    serve.add_argument("--port", default=None)

    args = parser.parse_args(argv)
    if args.cmd == "margin":
        return _cmd_margin(args)
    if args.cmd == "catalog":
        return _cmd_catalog(args)
    if args.cmd == "verify-host":
        return _cmd_verify(args)
    if args.cmd == "serve":
        return _cmd_serve(args)
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
