from __future__ import annotations

import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from isurvive import __version__
from isurvive.catalog import ROOT, catalog
from isurvive.checkout import (
    CheckoutError,
    checkout_enabled,
    create_checkout_session,
    parse_webhook,
)
from isurvive.dual_host import public_remotes, verify_tags
from isurvive.ollama_client import rewrite, status as ollama_status
from isurvive.situation import adapt, load_modules

WEB_DIR = ROOT / "web"
KITS_DIR = ROOT / "kits"


class SituationIn(BaseModel):
    setting: str = "woodland"
    climate: str = "mixed"
    hours: int = Field(default=24, ge=1, le=720)
    people: int = Field(default=1, ge=1, le=12)
    problems: list[str] = Field(default_factory=lambda: ["water", "shelter"])
    gear: list[str] = Field(default_factory=list)
    notes: str = ""
    use_local_model: bool = False


class CheckoutIn(BaseModel):
    sku: str
    quantity: int = Field(default=1, ge=1, le=20)


def create_app() -> FastAPI:
    env_file = ROOT / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_file)
        except ImportError:
            pass
    app = FastAPI(title="iSurvive", version=__version__)

    @app.get("/api/health")
    def health() -> dict:
        return {"ok": True, "version": __version__, "name": "iSurvive"}

    @app.get("/api/kits")
    def kits() -> dict:
        cat = catalog()
        return {
            "currency": cat.currency,
            "price_rule": cat.price_rule,
            "notes": cat.notes,
            "costing_as_of": cat.costing_as_of,
            "costing_status": cat.costing_status,
            "checkout_enabled": checkout_enabled(),
            "kits": [kit.public_dict() for kit in cat.kits],
        }

    @app.get("/api/kits/{sku}")
    def kit(sku: str) -> dict:
        try:
            return catalog().by_sku(sku).public_dict()
        except KeyError as exc:
            raise HTTPException(404, f"unknown SKU {sku}") from exc

    @app.get("/api/knowledge")
    def knowledge() -> dict:
        return {"modules": load_modules()}

    @app.post("/api/operator")
    def operator(payload: SituationIn) -> dict:
        situation = payload.model_dump()
        notes = situation.pop("notes", "")
        use_model = situation.pop("use_local_model", False)
        adapted = adapt(situation)
        if use_model:
            context = "\n\n".join(
                f"# {mod['title']}\n{mod['body']}" for mod in adapted["modules"]
            )
            prompt = (
                f"{situation} additional notes (do not store): {notes[:500]}"
                if notes
                else str(situation)
            )
            local = rewrite(prompt, context)
            if local:
                adapted["local_rewrite"] = local
                adapted["local_model"] = True
            else:
                adapted["local_model"] = False
                adapted["local_rewrite"] = None
        else:
            adapted["local_model"] = False
            adapted["local_rewrite"] = None
        return adapted

    @app.get("/api/hub")
    def hub() -> dict:
        names = public_remotes()
        origin_live = any("origin.cursor.com" in url for url in names.values())
        return {
            "ollama": ollama_status(),
            "checkout_enabled": checkout_enabled(),
            "remotes": names,
            "origin_configured": origin_live,
            "dual_host": "configured" if origin_live else "open",
        }

    @app.get("/api/dual-host")
    def dual_host() -> dict:
        return verify_tags()

    @app.post("/api/checkout")
    def checkout(payload: CheckoutIn) -> dict:
        try:
            kit = catalog().by_sku(payload.sku)
        except KeyError as exc:
            raise HTTPException(404, f"unknown SKU {payload.sku}") from exc
        base = os.environ.get("PUBLIC_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
        try:
            session = create_checkout_session(
                kit,
                quantity=payload.quantity,
                success_url=f"{base}/?checkout=success&sku={kit.sku}",
                cancel_url=f"{base}/?checkout=cancel&sku={kit.sku}",
            )
        except CheckoutError as exc:
            raise HTTPException(400, str(exc)) from exc
        return session

    @app.post("/api/stripe/webhook")
    async def stripe_webhook(request: Request) -> dict:
        payload = await request.body()
        signature = request.headers.get("stripe-signature", "")
        try:
            return parse_webhook(payload, signature)
        except CheckoutError as exc:
            raise HTTPException(503, str(exc)) from exc
        except Exception as exc:  # noqa: BLE001 — Stripe signature errors
            raise HTTPException(400, "invalid webhook") from exc

    @app.get("/api/drafts")
    def drafts() -> dict:
        folder = ROOT / "drafts" / "x"
        items = []
        for path in sorted(folder.glob("*.md")):
            items.append(
                {
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "title": path.stem,
                    "status": "steward draft",
                }
            )
        return {"publish": "human only", "account": "https://x.com/the_Arow_H", "drafts": items}

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(WEB_DIR / "index.html")

    app.mount("/kits", StaticFiles(directory=KITS_DIR), name="kits")
    app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
    return app


app = create_app()


def run_hub(host: str = "127.0.0.1", port: int = 8080) -> None:
    import uvicorn

    uvicorn.run("isurvive.hub:app", host=host, port=port, reload=False)
