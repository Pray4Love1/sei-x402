#!/usr/bin/env python3

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _select_path(data: Any, path: str | None) -> Any:
    if not path:
        return data

    current = data
    for segment in path.split("."):
        if isinstance(current, dict) and segment in current:
            current = current[segment]
        else:
            raise KeyError(f"Missing path segment: {segment}")
    return current


def _keccak_hash(payload: bytes) -> str:
    try:
        from eth_utils import keccak
    except ImportError as exc:  # pragma: no cover - handled in CLI
        raise RuntimeError("eth-utils is required for keccak hashing") from exc

    return "0x" + keccak(payload).hex()


def _sha256_hash(payload: bytes) -> str:
    return "0x" + hashlib.sha256(payload).hexdigest()


def _get_hasher(algorithm: str) -> Callable[[bytes], str]:
    if algorithm == "keccak":
        return _keccak_hash
    if algorithm == "sha256":
        return _sha256_hash
    raise ValueError(f"Unsupported algorithm: {algorithm}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute a deterministic Codex drop hash from JSON input."
    )
    parser.add_argument("codex_drop", type=Path, help="Path to a codex drop JSON file")
    parser.add_argument(
        "--json-path",
        default=None,
        help="Optional dot-delimited JSON path to hash (e.g. paymentPayload)",
    )
    parser.add_argument(
        "--algorithm",
        choices=["keccak", "sha256"],
        default="keccak",
        help="Hash algorithm to use",
    )
    parser.add_argument("--out", type=Path, default=None, help="Write hash to a file")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        raw = json.loads(args.codex_drop.read_text(encoding="utf-8"))
        selection = _select_path(raw, args.json_path)
        canonical = _canonical_json(selection)
        hasher = _get_hasher(args.algorithm)
        digest = hasher(canonical)
    except (OSError, json.JSONDecodeError, KeyError, ValueError, RuntimeError) as exc:
        print(f"[!] Failed to compute hash: {exc}", file=sys.stderr)
        return 1

    if args.out:
        args.out.write_text(digest + "\n", encoding="utf-8")

    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
