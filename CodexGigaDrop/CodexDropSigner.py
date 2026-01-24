#!/usr/bin/env python3
"""Sign Codex drop payloads with an HMAC-based signature."""

from __future__ import annotations

import argparse
import datetime as dt
import hmac
import hashlib
import json
import os
import sys
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()

SIGNATURE_SCHEME = "hmac-sha256"


def canonicalize_payload(payload: Dict[str, Any]) -> str:
    """Canonicalize JSON payload with sorted keys and compact separators."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def sign_payload(payload: Dict[str, Any], secret: str) -> str:
    """Return hex HMAC signature for the payload."""
    message = canonicalize_payload(payload).encode("utf-8")
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def build_signed_drop(payload: Dict[str, Any], secret: str) -> Dict[str, Any]:
    """Create a signed drop wrapper containing the payload and signature."""
    signature = sign_payload(payload, secret)
    return {
        "signatureScheme": SIGNATURE_SCHEME,
        "signature": signature,
        "signedAt": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "payload": payload,
    }


def load_payload(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Payload must be a JSON object")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Sign a Codex drop payload.")
    parser.add_argument("--input", required=True, help="Path to payload JSON")
    parser.add_argument("--output", help="Path to write signed payload")
    parser.add_argument(
        "--secret",
        help="Signing secret (defaults to CODEX_DROP_SECRET env var)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    args = parser.parse_args()

    secret = args.secret or os.getenv("CODEX_DROP_SECRET")
    if not secret:
        print("Missing signing secret. Set CODEX_DROP_SECRET or pass --secret.", file=sys.stderr)
        return 1

    try:
        payload = load_payload(args.input)
    except (OSError, ValueError) as exc:
        print(f"Failed to read payload: {exc}", file=sys.stderr)
        return 1

    signed = build_signed_drop(payload, secret)
    output_json = json.dumps(signed, indent=2 if args.pretty else None)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(output_json)
    else:
        print(output_json)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
