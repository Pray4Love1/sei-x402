"""Run a local autonomous x402 settlement simulation."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.adapter_evm import EVMAdapter
from offline.config import OPERATOR_KEY_PATH
from soul_sync.agent_credential import AgentCredential
from swarm.shard_executor import ShardExecutor
from swarm.swarm_root import SwarmRoot
from swarm.worker_agent import WorkerProfile


def ensure_local_signer_key(path: str) -> None:
    key_path = Path(path)
    if not key_path.exists():
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_text("bootstrap-local-signer-key\n", encoding="utf-8")


def adapter_registry() -> dict:
    """Universal adapter registry with EVM as the default enabled rail."""
    networks = [n.strip().upper() for n in os.getenv("X402_NETWORKS", "EVM").split(",") if n.strip()]
    registry = {}
    for network in networks:
        if network == "EVM":
            registry[network] = EVMAdapter("http://localhost:8545")
        else:
            registry[network] = EVMAdapter("http://localhost:8545")
            registry[network].name = f"GENERIC-{network}"
    return registry


async def main() -> None:
    adapters = adapter_registry()

    workers = [
        WorkerProfile(
            worker_id=f"0xDEAD{i:04X}",
            wage_per_hour=25 + (i % 10),
            hours_worked=30 + (i % 11),
            pto_allocated=80,
            pto_used=i % 8,
        )
        for i in range(250)
    ]

    root = SwarmRoot("epoch_12345", [w.worker_id for w in workers], list(adapters.keys()))
    intent = root.create_master_intent()
    print("[INTENT]", {"epoch": intent["epoch"], "employees": len(intent["employees"]), "networks": intent["networks"]})

    ensure_local_signer_key(OPERATOR_KEY_PATH)
    credential = AgentCredential(OPERATOR_KEY_PATH)
    shard_executor = ShardExecutor(adapters, credential)

    shard_size = 50
    for i in range(0, len(workers), shard_size):
        shard_workers = workers[i : i + shard_size]
        results = await shard_executor.execute_shard(shard_workers, intent["epoch"])
        print(f"Shard {i // shard_size} settled entries: {len(results)}")


if __name__ == "__main__":
    asyncio.run(main())
