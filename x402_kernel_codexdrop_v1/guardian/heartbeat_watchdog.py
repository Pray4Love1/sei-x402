"""Heartbeat watchdog that records guardian checks."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def record_heartbeat(path: str, address: str, entropy_hash: str) -> None:
    timestamp = datetime.utcnow().isoformat()
    entry = f"{timestamp} | {address} | {entropy_hash}\n"
    Path(path).write_text(entry, encoding="utf-8")
