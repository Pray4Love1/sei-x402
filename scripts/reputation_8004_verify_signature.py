#!/usr/bin/env python3
"""
Verify agent signatures for x402 8004-reputation InteractionData.
This script loads an ERC-8004 registration file, filters signers by
validity window, and verifies the interactionHash signature.
"""

from __future__ import annotations

import argparse
import binascii
import importlib
import importlib.util
import json
import sys
import time
from typing import Iterable, Optional, Tuple


def _strip_0x(value: str) -> str:
    return value[2:] if value.startswith("0x") else value


def _hex_to_bytes(name: str, value: str) -> bytes:
    try:
        return binascii.unhexlify(_strip_0x(value))
    except binascii.Error as exc:
        raise SystemExit(f"{name} must be valid hex") from exc


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


def _keccak256(data: bytes) -> bytes:
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


def _address_from_pubkey(pubkey_bytes: bytes) -> str:
    if len(pubkey_bytes) == 64:
        uncompressed = b"\x04" + pubkey_bytes
    elif len(pubkey_bytes) == 65 and pubkey_bytes[0] == 4:
        uncompressed = pubkey_bytes
    else:
        raise SystemExit("public-key must be 64-byte or 65-byte uncompressed hex")
    digest = _keccak256(uncompressed[1:])
    return "0x" + digest[-20:].hex()


def _recover_secp256k1_address(signature: bytes, msg_hash: bytes) -> Optional[str]:
    if importlib.util.find_spec("coincurve") is None:
        raise SystemExit("coincurve not installed (pip install coincurve)")
    PublicKey = importlib.import_module("coincurve").PublicKey

    if len(signature) != 65:
        return None

    recid = signature[64]
    if recid >= 27:
        recid -= 27
    if recid > 1:
        return None
    recoverable = signature[:64] + bytes([recid])

    try:
        pubkey = PublicKey.from_signature_and_message(recoverable, msg_hash, hasher=None)
    except Exception:
        return None

    return _address_from_pubkey(pubkey.format(compressed=False)[1:])


def verify_secp256k1(interaction_hash_hex: str, sig_hex: str, pubkey_hex: str) -> bool:
    msg_hash = _hex_to_bytes("interaction-hash", interaction_hash_hex)
    signature = _hex_to_bytes("agent-signature", sig_hex)
    pubkey_bytes = _hex_to_bytes("public-key", pubkey_hex)

    if len(pubkey_bytes) == 20:
        recovered = _recover_secp256k1_address(signature, msg_hash)
        if recovered is None:
            return False
        return recovered.lower() == ("0x" + pubkey_bytes.hex()).lower()

    if importlib.util.find_spec("coincurve") is None:
        raise SystemExit("coincurve not installed (pip install coincurve)")
    PublicKey = importlib.import_module("coincurve").PublicKey

    if len(pubkey_bytes) == 64:
        pubkey_bytes = b"\x04" + pubkey_bytes
    pubkey = PublicKey(pubkey_bytes)

    if len(signature) == 65:
        signature = signature[:64]

    if len(signature) == 64:
        return pubkey.verify(signature, msg_hash, hasher=None, sigdecode="compact")
    return pubkey.verify(signature, msg_hash, hasher=None)


def verify_ed25519(interaction_hash_hex: str, sig_hex: str, pubkey_hex: str) -> bool:
    if importlib.util.find_spec("nacl") is None:
        raise SystemExit("pynacl not installed (pip install pynacl)")
    nacl_exceptions = importlib.import_module("nacl.exceptions")
    nacl_signing = importlib.import_module("nacl.signing")
    BadSignatureError = nacl_exceptions.BadSignatureError
    VerifyKey = nacl_signing.VerifyKey

    msg_hash = _hex_to_bytes("interaction-hash", interaction_hash_hex)
    signature = _hex_to_bytes("agent-signature", sig_hex)
    pubkey = _hex_to_bytes("public-key", pubkey_hex)

    verify_key = VerifyKey(pubkey)
    try:
        verify_key.verify(msg_hash, signature)
        return True
    except BadSignatureError:
        return False


def _eligible_signers(signers: Iterable[dict], now: int) -> list[dict]:
    eligible = []
    for signer in signers:
        valid_from = signer.get("validFrom", 0)
        valid_until = signer.get("validUntil")
        if valid_from > now:
            continue
        if valid_until is not None and valid_until <= now:
            continue
        eligible.append(signer)
    return eligible


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify 8004-reputation signature.")
    parser.add_argument("--interaction-hash", required=True)
    parser.add_argument("--agent-signature", required=True)
    parser.add_argument("--registration-file", required=True)
    args = parser.parse_args()

    now = int(time.time())

    with open(args.registration_file, "r", encoding="utf-8") as handle:
        reg = json.load(handle)

    signers = reg.get("signers", [])
    eligible_signers = _eligible_signers(signers, now)

    if not eligible_signers:
        raise SystemExit("No valid signers available for verification.")

    for signer in eligible_signers:
        algo = signer.get("algorithm")
        pub = signer.get("publicKey")
        if not algo or not pub:
            continue

        if algo == "secp256k1":
            if verify_secp256k1(args.interaction_hash, args.agent_signature, pub):
                print("VALID")
                return
        elif algo == "ed25519":
            if verify_ed25519(args.interaction_hash, args.agent_signature, pub):
                print("VALID")
                return

    print("INVALID")
    sys.exit(1)


if __name__ == "__main__":
    main()
