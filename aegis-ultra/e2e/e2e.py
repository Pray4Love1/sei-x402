import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

sys.path.insert(0, os.path.join(ROOT, "core", "ai-risk-engine"))
sys.path.insert(0, os.path.join(ROOT, "core", "homomorphic"))
sys.path.insert(0, os.path.join(ROOT, "adapters", "coinbase-x402", "custody-guards"))

from risk_engine import build_fee_quote, score_payment  # noqa: E402
from homomorphic import aggregate_encrypted, encrypt_value  # noqa: E402
from guards import validate_custody  # noqa: E402


def run() -> dict:
    requirement = {"amount": "12500", "network": "base", "asset": "USDC"}
    metadata = {"fee_bps": 35, "facilitator": "x402-demo"}

    validate_custody(requirement)

    risk = score_payment(requirement, metadata)
    quote = build_fee_quote(requirement, risk)
    encrypted_total = aggregate_encrypted([encrypt_value(12.5), encrypt_value(3.25)])

    return {
        "risk_score": risk.score,
        "risk_reason": risk.reason,
        "risk_tags": risk.tags,
        "fee_quote": quote.__dict__,
        "encrypted_total": encrypted_total,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
