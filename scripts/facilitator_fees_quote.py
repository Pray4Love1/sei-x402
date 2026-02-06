#!/usr/bin/env python3
"""Canonicalize and hash facilitator fee quotes for signing."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import Any, Dict



def load_json(path: str) -> Dict[str, Any]:
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def strip_signature_fields(quote: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in quote.items()
        if key not in {"signature", "signatureScheme"}
    }


def canonicalize_quote(quote: Dict[str, Any]) -> str:
    stripped = strip_signature_fields(quote)
    return json.dumps(
        stripped,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

def keccak256(data: bytes) -> bytes:
    rate = 136
    capacity = 64
    assert rate + capacity == 200

    state = [0] * 25

    def _rotl(value: int, shift: int) -> int:
        return ((value << shift) | (value >> (64 - shift))) & 0xFFFFFFFFFFFFFFFF

    _ROTATION_OFFSETS = (
        (0, 36, 3, 41, 18),
        (1, 44, 10, 45, 2),
        (62, 6, 43, 15, 61),
        (28, 55, 25, 21, 56),
        (27, 20, 39, 8, 14),
    )

    _ROUND_CONSTANTS = (
        0x0000000000000001, 0x0000000000008082, 0x800000000000808A,
        0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
        0x8000000080008081, 0x8000000000008009, 0x000000000000008A,
        0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
        0x000000008000808B, 0x800000000000008B, 0x8000000000008089,
        0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
        0x000000000000800A, 0x800000008000000A, 0x8000000080008081,
        0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
    )

    def keccak_f():
        for rc in _ROUND_CONSTANTS:
            c = [state[x] ^ state[x+5] ^ state[x+10] ^ state[x+15] ^ state[x+20] for x in range(5)]
            d = [c[(x-1)%5] ^ _rotl(c[(x+1)%5], 1) for x in range(5)]
            for x in range(5):
                for y in range(0, 25, 5):
                    state[x+y] ^= d[x]

            b = [0]*25
            for x in range(5):
                for y in range(5):
                    idx = x + 5*y
                    rot = _ROTATION_OFFSETS[x][y]
                    b[y + 5*((2*x + 3*y) % 5)] = _rotl(state[idx], rot)

            for i in range(25):
                state[i] = b[i] ^ ((~b[(i+5)%25]) & b[(i+10)%25])

            state[0] ^= rc

    offset = 0
    while offset < len(data):
        block = data[offset:offset+rate]
        if len(block) < rate:
            block = block + b'\x01' + b'\x00'*(rate-len(block)-1) + b'\x80'
        for i in range(0, rate, 8):
            state[i//8] ^= int.from_bytes(block[i:i+8], "little")
        keccak_f()
        offset += rate

    return b"".join(state[i].to_bytes(8, "little") for i in range(4))


def hash_quote(canonical_json: str, scheme: str) -> bytes:
    payload = canonical_json.encode("utf-8")
    if scheme == "eip191":
        return keccak256(payload)
    if scheme == "ed25519":
        return hashlib.sha256(payload).digest()
    raise ValueError(f"Unsupported signature scheme: {scheme}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Canonicalize facilitator fee quotes and compute hashes."
    )
    parser.add_argument(
        "--input",
        default="-",
        help="Path to quote JSON (use '-' for stdin).",
    )
    parser.add_argument(
        "--scheme",
        choices=["eip191", "ed25519"],
        default="eip191",
        help="Signature scheme used for hashing.",
    )
    parser.add_argument(
        "--print-canonical",
        action="store_true",
        help="Print the canonical JSON used for hashing.",
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Emit a JSON object with canonical JSON and digest.",
    )
    args = parser.parse_args()

    quote = load_json(args.input)
    canonical_json = canonicalize_quote(quote)
    digest = hash_quote(canonical_json, args.scheme)
    digest_hex = f"0x{digest.hex()}"

    if args.output_json:
        payload = {
            "signatureScheme": args.scheme,
            "canonicalJson": canonical_json,
            "digest": digest_hex,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    if args.print_canonical:
        print(canonical_json)

    print(digest_hex)


if __name__ == "__main__":
    main()
