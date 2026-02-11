"""Independent verification path for signed offline payloads."""

from __future__ import annotations

import hashlib
import hmac
import json

try:
    from eth_account import Account  # type: ignore
    from eth_account.messages import encode_defunct  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback path
    Account = None
    encode_defunct = None


def verify_tx(signed_payload: dict, fallback_key: str | None = None) -> bool:
    """Recover signer and verify signature against payload content.

    Strict mode:
    - secp256k1 signatures require `eth_account` availability.
    - hmac-sha256-fallback signatures require `fallback_key`.
    """

    payload = signed_payload["payload"]
    signature = signed_payload["signature"]
    signer = signed_payload["signer"]
    payload_str = signed_payload.get(
        "payload_canonical",
        json.dumps(payload, separators=(",", ":"), sort_keys=True),
    )

    scheme = signed_payload.get("scheme", "secp256k1")

    if scheme == "hmac-sha256-fallback":
        if fallback_key is None:
            return False
        expected_signature = hmac.new(
            fallback_key.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        expected_signer = hashlib.sha256(fallback_key.encode("utf-8")).hexdigest()[:40]
        return hmac.compare_digest(expected_signature, signature) and hmac.compare_digest(
            signer, expected_signer
        )

    if Account is None or encode_defunct is None:
        return False

    encoded = encode_defunct(text=payload_str)
    recovered = Account.recover_message(encoded, signature=signature)
    return recovered.lower() == signer.lower()
