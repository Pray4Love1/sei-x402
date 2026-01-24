#!/usr/bin/env python3
"""Verify Codex drop payload signatures."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

from dotenv import load_dotenv

from CodexDropSigner import SIGNATURE_SCHEME, sign_payload

load_dotenv()


def load_signed_payload(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Signed payload must be a JSON object")
    return data


def verify_signed_drop(signed: Dict[str, Any], secret: str) -> bool:
    scheme = signed.get("signatureScheme")
    if scheme != SIGNATURE_SCHEME:
        raise ValueError(f"Unsupported signature scheme: {scheme}")

    payload = signed.get("payload")
    signature = signed.get("signature")
    if not isinstance(payload, dict) or not isinstance(signature, str):
        raise ValueError("Signed payload must include payload and signature")

    expected = sign_payload(payload, secret)
    return expected == signature


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a signed Codex drop payload.")
    parser.add_argument("--input", required=True, help="Path to signed payload JSON")
    parser.add_argument(
        "--secret",
        help="Signing secret (defaults to CODEX_DROP_SECRET env var)",
    )
    args = parser.parse_args()

    secret = args.secret or os.getenv("CODEX_DROP_SECRET")
    if not secret:
        print("Missing signing secret. Set CODEX_DROP_SECRET or pass --secret.", file=sys.stderr)
        return 1

    try:
        signed = load_signed_payload(args.input)
        valid = verify_signed_drop(signed, secret)
    except (OSError, ValueError) as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        return 1

    if valid:
        print("Signature valid")
        return 0

    print("Signature invalid", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
