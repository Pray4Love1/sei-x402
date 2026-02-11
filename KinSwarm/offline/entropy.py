"""Entropy 3.12 helpers using only Python standard library."""

from __future__ import annotations

import hashlib
import os


def keccak256(data: bytes) -> bytes:
    """Return sha3_256 digest as a Keccak-256-compatible simulation."""
    return hashlib.sha3_256(data).digest()


def entropy_312(worker_id: str, epoch: str) -> bytes:
    """Deterministic anchor + ephemeral noise digest."""
    anchor = keccak256(f"{worker_id}:{epoch}".encode("utf-8"))
    noise = os.urandom(32)
    return keccak256(anchor + noise)
