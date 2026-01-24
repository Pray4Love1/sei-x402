#!/usr/bin/env python3
"""Verify a sealed Codex drop payload."""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from CodexDropVerifier import load_signed_payload, verify_signed_drop

load_dotenv()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a signed Codex drop payload.")
    parser.add_argument(
        "--input",
        default=os.getenv("CODEX_DROP_SIGNED_OUTPUT"),
        help="Path to signed payload JSON",
    )
    parser.add_argument(
        "--secret",
        default=os.getenv("CODEX_DROP_SECRET"),
        help="Signing secret (defaults to CODEX_DROP_SECRET)",
    )
    args = parser.parse_args()

    if not args.input:
        print("Missing input path. Pass --input or set CODEX_DROP_SIGNED_OUTPUT.", file=sys.stderr)
        return 1
    if not args.secret:
        print("Missing signing secret. Set CODEX_DROP_SECRET.", file=sys.stderr)
        return 1

    try:
        signed = load_signed_payload(args.input)
        valid = verify_signed_drop(signed, args.secret)
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
