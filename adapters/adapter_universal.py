"""Universal adapter registry for x402 multi-network simulation."""

from __future__ import annotations

from adapters.adapter_cosmos import CosmosAdapter
from adapters.adapter_evm import EVMAdapter
from adapters.adapter_solana import SolanaAdapter
from adapters.adapter_utxo import UTXOAdapter


ADAPTER_FACTORIES = {
    "EVM": lambda rpc_url: EVMAdapter(rpc_url),
    "COSMOS": lambda rpc_url: CosmosAdapter(rpc_url),
    "SOLANA": lambda rpc_url: SolanaAdapter(rpc_url),
    "UTXO": lambda rpc_url: UTXOAdapter(rpc_url),
}


def build_adapter(network: str, rpc_url: str = "http://localhost:8545"):
    """Build a dedicated adapter by network name.

    Falls back to EVM adapter when a network is unknown.
    """

    normalized = network.strip().upper()
    factory = ADAPTER_FACTORIES.get(normalized, ADAPTER_FACTORIES["EVM"])
    return factory(rpc_url)
