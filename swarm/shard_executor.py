"""Shard-level executor for batched autonomous settlements."""

from __future__ import annotations

from adapters.adapter_base import AdapterBase
from swarm.worker_agent import WorkerAgent, WorkerProfile
from soul_sync.agent_credential import AgentCredential


class ShardExecutor:
    def __init__(self, adapters: dict[str, AdapterBase], agent_credential: AgentCredential):
        self.adapters = adapters
        self.credential = agent_credential

    async def execute_shard(self, worker_profiles: list[WorkerProfile], epoch_id: str) -> dict:
        results: dict[tuple[str, str], dict] = {}

        for worker in worker_profiles:
            agent = WorkerAgent(worker, self.credential)
            signed_tx = await agent.settle(epoch_id)

            if not agent.validate_settlement(signed_tx):
                results[(worker.worker_id, "verify")] = {"status": "invalid_signature"}
                continue

            for name, adapter in self.adapters.items():
                results[(worker.worker_id, name)] = adapter.send_tx(signed_tx)

        return results
