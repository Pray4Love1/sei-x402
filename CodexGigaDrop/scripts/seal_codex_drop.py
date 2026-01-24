#!/usr/bin/env python3
"""
seal_codex_drop.py - Seal a handoff JSON with deterministic digest + signature
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

import hashlib
from eth_account import Account
from eth_account.messages import encode_defunct


def keccak256(data: bytes) -> bytes:
    return hashlib.sha3_256(data).digest()


def canonical_json(obj: Dict[str, Any]) -> str:
    """Deterministic compact JSON (keys sorted, no extra whitespace)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_digest(payload: Dict[str, Any]) -> bytes:
    """Compute sealDigest = keccak256(canonical_json(payload))."""
    canon = canonical_json(payload).encode("utf-8")
    return keccak256(canon)


def sign_digest(digest: bytes, private_key: str) -> str:
    """Sign keccak256 digest using EIP-191 personal_sign style."""
    acc = Account.from_key(private_key)
    msg = encode_defunct(hexstr=digest.hex())
    signed = acc.sign_message(msg)
    return signed.signature.hex()


def seal_file(input_path: str, private_key: str, output_path: str) -> None:
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.is_file():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with input_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    payload = {k: v for k, v in data.items() if k not in ["codexMetadata", "sealSignature"]}

    digest = compute_digest(payload)
    digest_hex = digest.hex()

    signature = sign_digest(digest, private_key)

    if "codexMetadata" not in data:
        data["codexMetadata"] = {}
    data["codexMetadata"]["sealDigest"] = digest_hex
    data["codexMetadata"]["sealSignature"] = signature

    if "facilitatorFeeQuote" in data:
        quote = data["facilitatorFeeQuote"]
        quote_payload = {k: v for k, v in quote.items() if k not in ["signature", "quoteDigest"]}
        quote_digest = keccak256(canonical_json(quote_payload).encode("utf-8"))
        quote_sig = sign_digest(quote_digest, private_key)

        quote["quoteDigest"] = quote_digest.hex()
        quote["signature"] = quote_sig

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=False)

    print(f"[+] Sealed file written to: {output_path}")
    print(f"    sealDigest    = {digest_hex}")
    print(f"    sealSignature = {signature}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seal a JSON handoff with codex seal")
    parser.add_argument("input", help="Input JSON file (handoff.json)")
    parser.add_argument(
        "--private-key-file",
        default="attribution.key",
        help="File containing hex private key",
    )
    parser.add_argument("--private-key", help="Private key hex directly (insecure)")
    parser.add_argument("--out", required=True, help="Output sealed file (.codex.json)")

    args = parser.parse_args()

    if args.private_key:
        private_key = args.private_key
    else:
        pk_file = Path(args.private_key_file)
        if not pk_file.is_file():
            print(f"Error: Private key file not found: {pk_file}", file=sys.stderr)
            sys.exit(1)
        private_key = pk_file.read_text().strip()
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key

    seal_file(args.input, private_key, args.out)


if __name__ == "__main__":
    main()
