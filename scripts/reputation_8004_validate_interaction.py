#!/usr/bin/env python3
"""
Runtime validator for x402 8004-reputation InteractionData.
Validates:
- JSON Schema structure
- CAIP-style sanity checks
- interactionHash correctness
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Tuple

from jsonschema import Draft202012Validator


_ROTATION_OFFSETS: Tuple[Tuple[int, ...], ...] = (
    (0, 36, 3, 41, 18),
    (1, 44, 10, 45, 2),
    (62, 6, 43, 15, 61),
    (28, 55, 25, 21, 56),
    (27, 20, 39, 8, 14),
)

_ROUND_CONSTANTS: Tuple[int, ...] = (
    0x0000000000000001,
    0x0000000000008082,
    0x800000000000808A,
    0x8000000080008000,
    0x000000000000808B,
    0x0000000080000001,
    0x8000000080008081,
    0x8000000000008009,
    0x000000000000008A,
    0x0000000000000088,
    0x0000000080008009,
    0x000000008000000A,
    0x000000008000808B,
    0x800000000000008B,
    0x8000000000008089,
    0x8000000000008003,
    0x8000000000008002,
    0x8000000000000080,
    0x000000000000800A,
    0x800000008000000A,
    0x8000000080008081,
    0x8000000000008080,
    0x0000000080000001,
    0x8000000080008008,
)


def _rotl(value: int, shift: int) -> int:
    return ((value << shift) | (value >> (64 - shift))) & 0xFFFFFFFFFFFFFFFF


def keccak256(data: bytes) -> bytes:
    rate = 136  # bytes
    capacity = 64  # bytes
    assert rate + capacity == 200

    state = [0] * 25

    def keccak_f() -> None:
        for rc in _ROUND_CONSTANTS:
            c = [
                state[x]
                ^ state[x + 5]
                ^ state[x + 10]
                ^ state[x + 15]
                ^ state[x + 20]
                for x in range(5)
            ]
            d = [c[(x - 1) % 5] ^ _rotl(c[(x + 1) % 5], 1) for x in range(5)]
            for x in range(5):
                for y in range(0, 25, 5):
                    state[x + y] ^= d[x]

            b = [0] * 25
            for x in range(5):
                for y in range(5):
                    idx = x + 5 * y
                    rot = _ROTATION_OFFSETS[x][y]
                    new_x = y
                    new_y = (2 * x + 3 * y) % 5
                    b[new_x + 5 * new_y] = _rotl(state[idx], rot)

            for x in range(5):
                for y in range(5):
                    idx = x + 5 * y
                    state[idx] = b[idx] ^ (
                        (~b[((x + 1) % 5) + 5 * y]) & b[((x + 2) % 5) + 5 * y]
                    )

            state[0] ^= rc

    offset = 0
    while offset < len(data):
        block = data[offset : offset + rate]
        if len(block) < rate:
            block = bytearray(block)
            block.append(0x01)
            block.extend(b"\x00" * (rate - len(block) - 1))
            block.append(0x80)
        for i in range(0, len(block), 8):
            lane = int.from_bytes(block[i : i + 8], "little")
            state[i // 8] ^= lane
        keccak_f()
        offset += rate

    if len(data) % rate == 0:
        block = bytearray(rate)
        block[0] = 0x01
        block[-1] = 0x80
        for i in range(0, rate, 8):
            lane = int.from_bytes(block[i : i + 8], "little")
            state[i // 8] ^= lane
        keccak_f()

    output = bytearray()
    while len(output) < 32:
        for i in range(0, rate, 8):
            output.extend(state[i // 8].to_bytes(8, "little"))
            if len(output) >= 32:
                return bytes(output[:32])
        keccak_f()
    return bytes(output[:32])


def load_json(path: str) -> Dict[str, Any]:
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def compute_interaction_hash(task_ref: str, request_body: str, response_body: str) -> str:
    payload = (
        task_ref.encode("utf-8")
        + request_body.encode("utf-8")
        + response_body.encode("utf-8")
    )
    return "0x" + keccak256(payload).hex()


def validate_caip_prefix(network_id: str, task_ref: str) -> None:
    if not task_ref.startswith(network_id + ":"):
        raise SystemExit("taskRef does not match networkId (CAIP violation)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate 8004-reputation InteractionData"
    )
    parser.add_argument("--interaction", required=True, help="InteractionData JSON file")
    parser.add_argument("--schema", required=True, help="Schema JSON file")
    parser.add_argument("--request-body", required=True, help="Original request body")
    parser.add_argument("--response-body", required=True, help="Original response body")
    args = parser.parse_args()

    interaction = load_json(args.interaction)
    schema = load_json(args.schema)

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(interaction), key=lambda err: err.path)
    if errors:
        for err in errors:
            print(f"Schema error: {err.message}")
        sys.exit(1)

    validate_caip_prefix(interaction["networkId"], interaction["taskRef"])

    expected_hash = compute_interaction_hash(
        interaction["taskRef"],
        args.request_body,
        args.response_body,
    )

    if interaction["interactionHash"].lower() != expected_hash.lower():
        raise SystemExit(
            "interactionHash mismatch\n"
            f"expected: {expected_hash}\n"
            f"found:    {interaction['interactionHash']}"
        )

    print("VALID")
    sys.exit(0)


if __name__ == "__main__":
    main()
