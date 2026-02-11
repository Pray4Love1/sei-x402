"""Network submission client used by broadcaster (simulation mode)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone


class NodeClient:
    def submit(self, signed_tx: dict, network: str) -> dict:
        canonical = json.dumps(signed_tx, sort_keys=True)
        digest = hashlib.sha256(f"{network}:{canonical}".encode("utf-8")).hexdigest()
        payload = signed_tx.get("payload", {})
        return {
            "network": network,
            "tx_hash": digest,
            "status": "confirmed",
            "worker": payload.get("worker") or payload.get("destination"),
            "epoch": payload.get("id") or payload.get("epoch"),
            "amount": payload.get("amount"),
            "canonical_payload_hash": signed_tx.get("hash"),
            "signature_scheme": signed_tx.get("scheme"),
            "verification_result": bool(signed_tx.get("verification_result")),
            "timestamp": payload.get("timestamp") or datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
