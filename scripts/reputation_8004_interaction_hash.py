#!/usr/bin/env python3
"""
Compute interactionHash for x402 8004-reputation.
interactionHash = keccak256(
  UTF8(taskRef) || UTF8(requestBody) || UTF8(responseBody)
)
"""

from __future__ import annotations

import argparse
import json
from typing import Tuple


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
            c = [state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20] for x in range(5)]
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
                    state[idx] = b[idx] ^ ((~b[((x + 1) % 5) + 5 * y]) & b[((x + 2) % 5) + 5 * y])

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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute x402 8004-reputation interactionHash"
    )
    parser.add_argument("--task-ref", required=True)
    parser.add_argument("--request-body", default="")
    parser.add_argument("--response-body", default="")
    parser.add_argument("--output-json", action="store_true")

    args = parser.parse_args()

    payload = (
        args.task_ref.encode("utf-8")
        + args.request_body.encode("utf-8")
        + args.response_body.encode("utf-8")
    )

    digest = keccak256(payload)
    hex_digest = "0x" + digest.hex()

    if args.output_json:
        print(
            json.dumps(
                {
                    "taskRef": args.task_ref,
                    "interactionHash": hex_digest,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(hex_digest)


if __name__ == "__main__":
    main()
