from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
import hashlib
import hmac
import json
import os
import time
import uuid


@dataclass(frozen=True)
class RiskSignal:
    score: float
    reason: str
    tags: Dict[str, str]


@dataclass(frozen=True)
class FeeQuote:
    quote_id: str
    asset: str
    amount: str
    risk_score: float
    base_fee_bps: int
    risk_fee_bps: int
    total_fee_bps: int
    expires_at: int
    policy_hash: str
    signature: str


def score_payment(requirement: Dict[str, Any], facilitator_metadata: Dict[str, Any]) -> RiskSignal:
    """Return a deterministic risk score for an x402 payment requirement."""
    amount = float(requirement.get("amount", 0))
    fee_bps = float(facilitator_metadata.get("fee_bps", 0))
    score = min(1.0, (amount / 10_000) + (fee_bps / 10_000))

    return RiskSignal(
        score=score,
        reason="baseline_fee_and_amount",
        tags={"network": str(requirement.get("network", "unknown"))},
    )


def price_fee(risk_score: float) -> Dict[str, int]:
    base_bps = 10
    risk_bps = int(min(90, risk_score * 50))
    return {
        "base_fee_bps": base_bps,
        "risk_fee_bps": risk_bps,
        "total_fee_bps": base_bps + risk_bps,
    }


def _policy_hash(policy: Dict[str, Any]) -> str:
    payload = json.dumps(policy, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _sign_payload(payload: Dict[str, Any]) -> str:
    secret = os.getenv("AEGIS_SIGNING_SECRET", "local-dev-secret").encode("utf-8")
    serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hmac.new(secret, serialized, hashlib.sha256).hexdigest()


def build_fee_quote(requirement: Dict[str, Any], risk: RiskSignal) -> FeeQuote:
    policy = {"risk_model": "baseline", "pricing": "base_plus_risk"}
    policy_hash = _policy_hash(policy)
    fees = price_fee(risk.score)
    expires_at = int(time.time()) + 300

    payload = {
        "asset": requirement.get("asset", "USDC"),
        "amount": requirement.get("amount", "0"),
        "risk_score": risk.score,
        **fees,
        "expires_at": expires_at,
        "policy_hash": policy_hash,
    }

    signature = _sign_payload(payload)

    return FeeQuote(
        quote_id=str(uuid.uuid4()),
        asset=payload["asset"],
        amount=payload["amount"],
        risk_score=payload["risk_score"],
        base_fee_bps=payload["base_fee_bps"],
        risk_fee_bps=payload["risk_fee_bps"],
        total_fee_bps=payload["total_fee_bps"],
        expires_at=payload["expires_at"],
        policy_hash=payload["policy_hash"],
        signature=signature,
    )
