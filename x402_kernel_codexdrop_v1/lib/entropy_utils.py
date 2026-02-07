"""Entropy and mnemonic helpers for the x402 kernel drop."""

from __future__ import annotations

import hashlib

from mnemonic import Mnemonic


def generate_entropy(username: str, pin: str, guardians: list[str], salt: str) -> bytes:
    preimage = f"{username}:{pin}:{','.join(guardians)}:{salt}"
    return hashlib.sha256(preimage.encode("utf-8")).digest()


def generate_mnemonic(entropy: bytes) -> str:
    return Mnemonic("english").to_mnemonic(entropy)


def derive_root_seed(mnemonic: str, passphrase: str = "") -> bytes:
    return Mnemonic.to_seed(mnemonic, passphrase)
