"""Base adapter interfaces for multi-network settlement simulation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AdapterBase(ABC):
    """Network adapter contract for swarm submission paths."""

    name: str

    @abstractmethod
    def send_tx(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Submit a signed payload and return a submission receipt."""

    @abstractmethod
    def estimate_fee(self, payload: dict[str, Any]) -> int:
        """Estimate fee units for this payload on the target network."""

    @abstractmethod
    def get_balance(self, address: str) -> int:
        """Return a mocked or real balance for an address."""
