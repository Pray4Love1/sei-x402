"""x402 protocol conformance helpers.

Maps canonical `X-PAYMENT`/`X-PAYMENT-RESPONSE` headers to and from the
internal settlement model used by this runtime.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from hashlib import sha256
from typing import Any


@dataclass(frozen=True)
class InternalSettlement:
    intent: str
    epoch: str
    worker: str
    amount: int
    network: str
    x402_version: int
    scheme: str
    payment_payload: dict[str, Any]


def _b64_decode_json(value: str) -> dict[str, Any]:
    decoded = base64.b64decode(value.encode("utf-8"))
    return json.loads(decoded.decode("utf-8"))


def _b64_encode_json(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return base64.b64encode(canonical.encode("utf-8")).decode("utf-8")


def parse_x402_headers(headers: dict[str, str]) -> dict[str, str | None]:
    """Extract normalized x402 fields from raw HTTP headers."""
    return {
        "intent": headers.get("X-402-Intent"),
        "epoch": headers.get("X-402-Epoch"),
        "amount": headers.get("X-402-Amount"),
        "destination": headers.get("X-402-Destination"),
        "network": headers.get("X-402-Network") or headers.get("X-402-Network-Preference"),
        "entropy_312": headers.get("X-402-Entropy-312"),
        "agent_entropy": headers.get("X-402-Agent-Entropy"),
        "agent_token": headers.get("X-402-Agent-Token"),
    }


def decode_x_payment_header(x_payment_header: str) -> dict[str, Any]:
    """Decode canonical `X-PAYMENT` header content (base64 json)."""
    decoded = _b64_decode_json(x_payment_header)
    required_keys = {"x402Version", "scheme", "network", "payload"}
    missing = sorted(required_keys.difference(decoded.keys()))
    if missing:
        raise ValueError(f"X-PAYMENT missing keys: {','.join(missing)}")
    return decoded


def map_payment_payload_to_internal_settlement(
    x_payment_header: str,
    *,
    intent: str,
    epoch: str,
    worker: str,
) -> InternalSettlement:
    """Map canonical x402 payment payload to internal settlement model."""
    payment = decode_x_payment_header(x_payment_header)
    payload = payment["payload"]
    amount = int(payload["amount"])
    return InternalSettlement(
        intent=intent,
        epoch=str(epoch),
        worker=worker,
        amount=amount,
        network=str(payment["network"]).upper(),
        x402_version=int(payment["x402Version"]),
        scheme=str(payment["scheme"]),
        payment_payload=payload,
    )


def map_internal_settlement_to_payment_response(
    settlement: InternalSettlement,
    *,
    tx_hash: str,
    verification_result: bool,
) -> dict[str, Any]:
    """Create canonical `X-PAYMENT-RESPONSE` JSON payload from settlement data."""
    canonical_payload = {
        "x402Version": settlement.x402_version,
        "scheme": settlement.scheme,
        "network": settlement.network.lower(),
        "txHash": tx_hash,
        "success": bool(verification_result),
        "amount": str(settlement.amount),
        "worker": settlement.worker,
        "epoch": settlement.epoch,
        "payloadHash": sha256(
            json.dumps(settlement.payment_payload, separators=(",", ":"), sort_keys=True).encode(
                "utf-8"
            )
        ).hexdigest(),
    }
    return canonical_payload


def encode_x_payment_response(response_payload: dict[str, Any]) -> str:
    """Encode canonical `X-PAYMENT-RESPONSE` header content (base64 json)."""
    return _b64_encode_json(response_payload)
