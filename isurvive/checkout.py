from __future__ import annotations

import os
import secrets
import string

import stripe

from isurvive.catalog import Kit
from isurvive.costing import evaluate_kit


class CheckoutError(RuntimeError):
    pass


def stripe_key() -> str:
    return os.environ.get("STRIPE_SECRET_KEY", "").strip()


def checkout_enabled() -> bool:
    return bool(stripe_key())


def _identifier() -> str:
    suffix = "".join(secrets.choice(string.ascii_lowercase) for _ in range(8))
    return f"isurvive_kit_{suffix}"


def create_checkout_session(
    kit: Kit,
    *,
    quantity: int,
    success_url: str,
    cancel_url: str,
) -> dict:
    check = evaluate_kit(kit)
    if not check.ok:
        raise CheckoutError(
            f"{kit.sku} fails margin rule price >= landed / 0.70 "
            f"(min {check.min_price_cents} cents)"
        )
    if quantity < 1 or quantity > 20:
        raise CheckoutError("quantity must be 1–20")
    if not checkout_enabled():
        raise CheckoutError("STRIPE_SECRET_KEY is not set")

    client = stripe.StripeClient(
        stripe_key(),
        stripe_version="2026-07-29.dahlia",
    )
    session = client.v1.checkout.sessions.create(
        {
            "mode": "payment",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "client_reference_id": kit.sku,
            "integration_identifier": _identifier(),
            "shipping_address_collection": {"allowed_countries": ["US", "CA"]},
            "metadata": {
                "sku": kit.sku,
                "landed_cents": str(kit.landed_cents),
                "price_cents": str(kit.price_cents),
            },
            "line_items": [
                {
                    "quantity": quantity,
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": kit.price_cents,
                        "product_data": {
                            "name": f"{kit.sku} {kit.name}",
                            "description": kit.summary[:500],
                            "metadata": {"sku": kit.sku},
                        },
                    },
                }
            ],
        }
    )
    return {"id": session.id, "url": session.url}
