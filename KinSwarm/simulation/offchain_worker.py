"""Epoch settlement worker for local x402 simulation."""

from __future__ import annotations

import asyncio

from ledger import Ledger, LedgerRecord
from worker_profile import WorkerProfile


class OffchainWorker:
    def __init__(self, workers: list[WorkerProfile], adapters: list[object], ledger: Ledger) -> None:
        self.workers = workers
        self.adapters = adapters
        self.ledger = ledger

    async def settle_worker(self, worker: WorkerProfile, wallet_id: str, signed_record: dict) -> None:
        payload_bytes = signed_record["signed_payload"]["payload_canonical"].encode("utf-8")
        receipts = await asyncio.gather(*[adapter.send(payload_bytes) for adapter in self.adapters])

        for receipt in receipts:
            self.ledger.record(
                LedgerRecord(
                    worker_name=worker.name,
                    wallet_id=wallet_id,
                    epoch=int(signed_record["epoch"]),
                    amount=int(signed_record["amount"]),
                    canonical_payload_hash=signed_record["canonical_payload_hash"],
                    signature_scheme=signed_record["signature_scheme"],
                    verification_result=bool(signed_record["verification_result"]),
                    timestamp=signed_record["timestamp"],
                    network=receipt["network"],
                    tx_hash=receipt["tx_hash"],
                )
            )

    async def settle_epoch(self, records: list[dict], epoch_id: int, batch_size: int = 300) -> None:
        print(f"Settling x402 epoch {epoch_id} for {len(records)} workers...")
        tasks = [self.settle_worker(row["worker"], row["wallet_id"], row) for row in records]
        for i in range(0, len(tasks), batch_size):
            await asyncio.gather(*tasks[i : i + batch_size])
