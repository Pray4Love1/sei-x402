#!/usr/bin/env python3
"""Submit signed Codex drop payloads in batch."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Iterable, List

import requests
from dotenv import load_dotenv

load_dotenv()


def load_batch(path: str) -> List[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data

    raise ValueError("Batch file must be a JSON object or array")


def submit_batch(endpoint: str, batch: Iterable[dict[str, Any]], timeout: float) -> int:
    failures = 0
    for index, payload in enumerate(batch, start=1):
        try:
            response = requests.post(endpoint, json=payload, timeout=timeout)
            if response.status_code >= 400:
                failures += 1
                print(
                    f"[{index}] Failed ({response.status_code}): {response.text}",
                    file=sys.stderr,
                )
            else:
                print(f"[{index}] Submitted ({response.status_code})")
        except requests.RequestException as exc:
            failures += 1
            print(f"[{index}] Request failed: {exc}", file=sys.stderr)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit signed Codex drop payloads.")
    parser.add_argument("--input", required=True, help="Path to signed payload JSON")
    parser.add_argument(
        "--endpoint",
        default=os.getenv("CODEX_GIGADROP_ENDPOINT"),
        help="Submission endpoint URL",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Request timeout in seconds",
    )
    args = parser.parse_args()

    if not args.endpoint:
        print("Missing endpoint. Set CODEX_GIGADROP_ENDPOINT or pass --endpoint.", file=sys.stderr)
        return 1

    try:
        batch = load_batch(args.input)
    except (OSError, ValueError) as exc:
        print(f"Failed to read batch: {exc}", file=sys.stderr)
        return 1

    failures = submit_batch(args.endpoint, batch, args.timeout)
    if failures:
        print(f"Batch submission completed with {failures} failures", file=sys.stderr)
        return 1

    print("Batch submission completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
