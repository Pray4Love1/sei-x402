"""Offline orchestration harness for Entropy 3.12 signing + verification."""

from __future__ import annotations

import os

from config import OPERATOR_KEY_PATH
from entropy import entropy_for_header, keccak256
from signer import OfflineSigner
from verify import verify_tx


def eth_digest(message: bytes) -> bytes:
    prefix = f"\x19Ethereum Signed Message:\n{len(message)}".encode("utf-8")
    return keccak256(prefix + message)


if __name__ == "__main__":
    user = "0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF"
    header_id = "header_12345"
    state_value = 42
    session_noise = os.urandom(16).hex()

    entropy_val = entropy_for_header(header_id)
    print(f"[ENTROPY 3.12] {entropy_val.hex()}")

    payload_bytes = f"{user}:{header_id}:{state_value}:{session_noise}".encode("utf-8")
    digest = eth_digest(payload_bytes)
    print(f"[DIGEST] {digest.hex()}")

    signer = OfflineSigner(OPERATOR_KEY_PATH)
    signed_tx = signer.build_signed_tx(
        {
            "id": header_id,
            "destination": user,
            "amount": state_value,
            "entropy": entropy_val.hex(),
        }
    )
    print("[SIGNED TX]", signed_tx)

    verified = verify_tx(signed_tx, fallback_key=signer.private_key)
    print(f"[VERIFIED] {verified}")
