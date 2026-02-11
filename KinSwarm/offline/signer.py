"""Offline signer for simulation-safe payload signing without network dependencies."""

from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path


class OfflineSigner:
    """HMAC-based simulation signer (no RPC, no network dependency)."""

    def __init__(self, key_path: str):
        self.key = Path(key_path).read_text(encoding="utf-8").strip().encode("utf-8")
        self.signer_id = hashlib.sha256(self.key).hexdigest()[:40]

    @staticmethod
    def _canonical(payload: dict) -> str:
        return json.dumps(payload, separators=(",", ":"), sort_keys=True)

    def sign(self, payload: dict) -> dict:
        canonical = self._canonical(payload)
        signature = hmac.new(self.key, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
        return {
            "payload": payload,
            "payload_canonical": canonical,
            "signature": signature,
            "signer": self.signer_id,
        }

    def verify(self, signed_payload: dict) -> bool:
        canonical = signed_payload.get("payload_canonical") or self._canonical(signed_payload["payload"])
        expected = hmac.new(self.key, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signed_payload.get("signature", ""))
