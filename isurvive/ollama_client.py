from __future__ import annotations

import os

import httpx

DEFAULT_HOST = "http://127.0.0.1:11434"
DEFAULT_MODEL = "llama3.2"


def ollama_host() -> str:
    return os.environ.get("OLLAMA_HOST", DEFAULT_HOST).rstrip("/")


def ollama_model() -> str:
    return os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)


def status() -> dict:
    host = ollama_host()
    try:
        response = httpx.get(f"{host}/api/tags", timeout=2.0)
        response.raise_for_status()
        names = [item.get("name") for item in response.json().get("models") or []]
        return {
            "ok": True,
            "host": host,
            "model": ollama_model(),
            "models": names,
        }
    except Exception as exc:  # noqa: BLE001 — hub status must never crash the page
        return {
            "ok": False,
            "host": host,
            "model": ollama_model(),
            "error": str(exc),
        }


def rewrite(prompt: str, context: str) -> str | None:
    payload = {
        "model": ollama_model(),
        "stream": False,
        "prompt": (
            "You are the iSurvive Field Kit Operator. Stay on-device. "
            "Do not give medical treatment instructions. "
            "Adapt the field notes to the situation. Be concrete and short.\n\n"
            f"SITUATION:\n{prompt}\n\nFIELD NOTES:\n{context}\n"
        ),
    }
    try:
        response = httpx.post(
            f"{ollama_host()}/api/generate",
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json().get("response")
    except Exception:
        return None
