#!/usr/bin/env python3
"""
verify_codex_drop.py - Verify sealed codex drop
"""

import argparse
import json
import sys
from pathlib import Path

from eth_account import Account
from eth_account.messages import encode_defunct


def keccak256(data: bytes) -> bytes:
    from hashlib import sha3_256

    return sha3_256(data).digest()


def recover_signer(message: bytes, signature: str) -> str:
    msg = encode_defunct(message)
    acc = Account.recover_message(msg, signature=signature)
    return acc


def verify_file(file_path: str, expected_signer: str | None = None) -> None:
    path = Path(file_path)
    if not path.is_file():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    metadata = data.get("codexMetadata", {})
    seal_digest = metadata.get("sealDigest")
    seal_sig = metadata.get("sealSignature")

    if not seal_digest or not seal_sig:
        print("[✗] Missing sealDigest or sealSignature")
        sys.exit(1)

    payload = {k: v for k, v in data.items() if k != "codexMetadata"}
    computed_digest = keccak256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    computed_hex = computed_digest.hex()

    if computed_hex != seal_digest:
        print("[✗] Digest mismatch!")
        print(f"  Computed: {computed_hex}")
        print(f"  In file : {seal_digest}")
        sys.exit(1)

    recovered = recover_signer(computed_digest, seal_sig)

    print("[✓] Digest matches")
    print(f"[✓] Recovered signer: {recovered}")

    if expected_signer:
        if recovered.lower() != expected_signer.lower():
            print(f"[✗] Signer mismatch! Expected {expected_signer}, got {recovered}")
            sys.exit(1)
        print(f"[✓] Signer matches expected: {expected_signer}")

    if "facilitatorFeeQuote" in data:
        quote = data["facilitatorFeeQuote"]
        qsig = quote.get("signature")
        qdigest = quote.get("quoteDigest")
        if qsig and qdigest:
            qpayload = {k: v for k, v in quote.items() if k not in ["signature", "quoteDigest"]}
            canon = json.dumps(qpayload, sort_keys=True, separators=(",", ":")).encode("utf-8")
            comp_qd = keccak256(canon).hex()
            if comp_qd == qdigest:
                qsigner = recover_signer(keccak256(canon), qsig)
                print(f"[✓] Fee quote digest valid, signed by: {qsigner}")
            else:
                print("[✗] Fee quote digest mismatch")

    print("[✓] All basic checks passed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify sealed codex drop")
    parser.add_argument("file", help="Sealed .codex.json file")
    parser.add_argument("--expected-signer", help="Expected signer address (0x...)")
    args = parser.parse_args()

    verify_file(args.file, args.expected_signer)


if __name__ == "__main__":
    main()
