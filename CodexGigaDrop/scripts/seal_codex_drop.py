#!/usr/bin/env python3
"""Seal (sign) a Codex drop payload using shared HMAC secret."""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from CodexDropSigner import build_signed_drop, load_payload

load_dotenv()


def main() -> int:
    parser = argparse.ArgumentParser(description="Seal (sign) a Codex drop payload.")
    parser.add_argument(
        "--input",
        default=os.getenv("CODEX_DROP_INPUT"),
        help="Path to unsigned payload JSON",
    )
    parser.add_argument(
        "--output",
        default=os.getenv("CODEX_DROP_SIGNED_OUTPUT"),
        help="Path to write signed payload JSON",
    )
    parser.add_argument(
        "--secret",
        default=os.getenv("CODEX_DROP_SECRET"),
        help="Signing secret (defaults to CODEX_DROP_SECRET)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    args = parser.parse_args()

    if not args.input:
        print("Missing input path. Pass --input or set CODEX_DROP_INPUT.", file=sys.stderr)
        return 1
    if not args.output:
        print("Missing output path. Pass --output or set CODEX_DROP_SIGNED_OUTPUT.", file=sys.stderr)
        return 1
    if not args.secret:
        print("Missing signing secret. Set CODEX_DROP_SECRET.", file=sys.stderr)
        return 1

    try:
        payload = load_payload(args.input)
    except (OSError, ValueError) as exc:
        print(f"Failed to read payload: {exc}", file=sys.stderr)
        return 1

    signed = build_signed_drop(payload, args.secret)

    import json

    output_json = json.dumps(signed, indent=2 if args.pretty else None)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(output_json)

    print(f"Signed payload written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
