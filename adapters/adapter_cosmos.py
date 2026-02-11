"""x402 Cosmos-rail adapter mock for offline simulation."""

from __future__ import annotations

from hashlib import sha3_256
from typing import Any

from adapters.adapter_base import AdapterBase


class CosmosAdapter(AdapterBase):
    name = "COSMOS"

    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url

    def send_tx(self, payload: dict[str, Any]) -> dict[str, Any]:
        digest_source = payload.get("hash", str(payload))
        tx_hash = sha3_256(f"{self.name}:{digest_source}".encode("utf-8")).hexdigest()
        return {"network": self.name, "status": "simulated", "tx_hash": tx_hash}

    def estimate_fee(self, payload: dict[str, Any]) -> int:
        return 5_000 + len(str(payload))

    def get_balance(self, address: str) -> int:
        return 10**9
