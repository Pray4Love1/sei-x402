"""Offline signing helpers for Entropy 3.12 payloads.

Uses secp256k1 (`eth_account`) when available and a deterministic HMAC fallback
when the dependency is unavailable in restricted environments.
"""

from __future__ import annotations

import hashlib
import hmac
import json

try:
    from eth_account import Account  # type: ignore
    from eth_account.messages import encode_defunct  # type: ignore
    from web3 import Web3  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback path
    Account = None
    encode_defunct = None
    Web3 = None


class OfflineSigner:
    """Signs payload dictionaries with an operator private key."""

    def __init__(self, key_path: str):
        with open(key_path, "r", encoding="utf-8") as key_file:
            self.private_key = key_file.read().strip()
        if Account is not None:
            self.account = Account.from_key(self.private_key)
            self.signer = self.account.address
        else:
            self.account = None
            self.signer = hashlib.sha256(self.private_key.encode("utf-8")).hexdigest()[:40]

    @staticmethod
    def _canonical_payload(payload: dict) -> str:
        return json.dumps(payload, separators=(",", ":"), sort_keys=True)

    def build_signed_tx(self, payload: dict) -> dict:
        payload_str = self._canonical_payload(payload)

        if Account is not None and encode_defunct is not None and Web3 is not None:
            encoded = encode_defunct(text=payload_str)
            signed = Account.sign_message(encoded, self.private_key)
            signature = signed.signature.hex()
            digest_hash = Web3.keccak(text=payload_str).hex()
            scheme = "secp256k1"
        else:
            signature = hmac.new(
                self.private_key.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256
            ).hexdigest()
            digest_hash = hashlib.sha3_256(payload_str.encode("utf-8")).hexdigest()
            scheme = "hmac-sha256-fallback"

        return {
            "payload": payload,
            "payload_canonical": payload_str,
            "signature": signature,
            "signer": self.signer,
            "hash": digest_hash,
            "scheme": scheme,
        }
