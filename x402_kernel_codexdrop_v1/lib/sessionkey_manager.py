"""Ephemeral session key utilities."""

from __future__ import annotations

import hashlib


def derive_session_key(seed_hex: str, index: int) -> str:
    payload = f"{seed_hex}:{index}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def rotate_index(current_index: int) -> int:
    return current_index + 1
