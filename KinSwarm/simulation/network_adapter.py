"""Offline x402 network adapters for async simulation.

EVM remains the default rail, while Cosmos/Solana/UTXO are first-class
and can be enabled via `X402_NETWORKS`.
"""

from __future__ import annotations

import asyncio
import hashlib


class UniversalNetworkAdapter:
    def __init__(self, network: str = "x402:evm"):
        self.network = network.lower()

    async def send(self, payload: bytes) -> dict:
        await asyncio.sleep(0.0001)
        tx_hash = hashlib.sha256(self.network.encode("utf-8") + payload).hexdigest()
        return {"network": self.network, "tx_hash": tx_hash, "status": "confirmed"}


class EVMAdapter(UniversalNetworkAdapter):
    def __init__(self) -> None:
        super().__init__("x402:evm")


class CosmosAdapter(UniversalNetworkAdapter):
    def __init__(self) -> None:
        super().__init__("x402:cosmos")


class SolanaAdapter(UniversalNetworkAdapter):
    def __init__(self) -> None:
        super().__init__("x402:solana")


class UTXOAdapter(UniversalNetworkAdapter):
    def __init__(self) -> None:
        super().__init__("x402:utxo")


def build_simulation_adapters(networks: list[str]) -> list[UniversalNetworkAdapter]:
    """Build simulation adapters from canonical network names."""

    mapping = {
        "EVM": EVMAdapter,
        "COSMOS": CosmosAdapter,
        "SOLANA": SolanaAdapter,
        "UTXO": UTXOAdapter,
    }
    adapters: list[UniversalNetworkAdapter] = []
    for network in networks:
        adapter_cls = mapping.get(network.strip().upper(), EVMAdapter)
        adapters.append(adapter_cls())
    return adapters
