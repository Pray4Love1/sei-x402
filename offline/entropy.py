"""Entropy 3.12 offline primitives.

This module combines a deterministic header anchor with optional session noise
and then hashes the combination to produce irreversible entropy material.
It prefers `pycryptodome` Keccak when available and gracefully falls back to
`hashlib.sha3_256` in restricted environments.
"""

from __future__ import annotations

import hashlib
import os

try:
    from Crypto.Hash import keccak  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback path
    keccak = None


def keccak256(payload: bytes) -> bytes:
    """Return a Keccak-256-compatible digest for the given payload bytes."""
    if keccak is not None:
        digest = keccak.new(digest_bits=256)
        digest.update(payload)
        return digest.digest()
    return hashlib.sha3_256(payload).digest()


def entropy_for_header(header_id: str, session_noise: bytes | None = None) -> bytes:
    """Generate entropy commitment bytes for a header/session pair."""
    if session_noise is None:
        session_noise = os.urandom(32)

    anchor = keccak256(header_id.encode("utf-8"))
    return keccak256(anchor + session_noise)


def entropy_hex(header_id: str) -> str:
    """Return entropy commitment as a hex string for convenience."""
    return entropy_for_header(header_id).hex()
