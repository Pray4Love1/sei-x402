"""Autonomous x402-native payroll manager with shard-based settlement simulation."""

from __future__ import annotations

import asyncio
import csv
from dataclasses import dataclass
from pathlib import Path

from KinSwarm.config import (
    DEFAULT_NETWORKS,
    MAX_CONCURRENT_SHARDS,
    MAX_SHARD_SIZE,
    OPERATOR_KEY_PATH,
    PAYROLL_EPOCH,
)
from KinSwarm.offline.x402_reader import (
    encode_x_payment_response,
    map_internal_settlement_to_payment_response,
    map_payment_payload_to_internal_settlement,
)
from KinSwarm.online.full_pipeline import dispatch
from soul_sync.agent_credential import AgentCredential
from soul_sync.agent_verifier import AgentVerifier


@dataclass
class Worker:
    id: str
    wage: int
    hours: int
    pto_total: int
    pto_used: int

    def net_pay(self) -> int:
        paid_pto = min(self.pto_used, self.pto_total)
        return (self.hours + paid_pto) * self.wage

    def pto_remaining(self) -> int:
        return max(self.pto_total - self.pto_used, 0)


class SwarmManager:
    def __init__(self, workers: list[Worker]):
        self.workers = workers
        self.credential = AgentCredential(OPERATOR_KEY_PATH)

    @staticmethod
    def _x_payment_header(amount: int) -> str:
        import base64
        import json

        payload = {
            "x402Version": 1,
            "scheme": "exact",
            "network": "base-sepolia",
            "payload": {"amount": str(amount), "asset": "USDC", "resource": "/x402/payroll"},
        }
        canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return base64.b64encode(canonical).decode("utf-8")

    async def process_shard(self, shard: list[Worker]) -> list[dict]:
        signed_payloads: list[dict] = []

        for worker in shard:
            amount = worker.net_pay()
            payment_header = self._x_payment_header(amount)
            settlement = map_payment_payload_to_internal_settlement(
                payment_header,
                intent="x402.payroll.settle",
                epoch=PAYROLL_EPOCH,
                worker=worker.id,
            )

            signed = await self.credential.sign_payload(
                {
                    "id": PAYROLL_EPOCH,
                    "worker": worker.id,
                    "amount": settlement.amount,
                    "hours": worker.hours,
                    "pto_used": worker.pto_used,
                    "pto_remaining": worker.pto_remaining(),
                    "network": "x402:universal",
                }
            )
            signed["verification_result"] = AgentVerifier.verify(
                signed,
                fallback_key=self.credential.verification_key,
            )

            response_payload = map_internal_settlement_to_payment_response(
                settlement,
                tx_hash=signed["hash"],
                verification_result=signed["verification_result"],
            )
            signed["x_payment"] = payment_header
            signed["x_payment_response"] = encode_x_payment_response(response_payload)
            signed_payloads.append(signed)

        return dispatch(signed_payloads, DEFAULT_NETWORKS)

    async def run(self) -> list[dict]:
        shards = [self.workers[i : i + MAX_SHARD_SIZE] for i in range(0, len(self.workers), MAX_SHARD_SIZE)]
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_SHARDS)

        async def guarded(shard: list[Worker]) -> list[dict]:
            async with semaphore:
                return await self.process_shard(shard)

        nested_results = await asyncio.gather(*[guarded(shard) for shard in shards])
        results = [row for shard_result in nested_results for row in shard_result]
        assert results, "no settlement receipts generated"
        assert all(row["verification_result"] for row in results), "verification failure in receipts"
        return results


def build_demo_workers(size: int = 200) -> list[Worker]:
    workers = []
    for i in range(size):
        workers.append(
            Worker(
                id=f"did:x402:0xDEAD{i:06X}",
                wage=25 + (i % 8),
                hours=32 + (i % 12),
                pto_total=80,
                pto_used=i % 10,
            )
        )
    return workers


def write_ledger(rows: list[dict], path: str = "KinSwarm/ledger/x402_settlement_log.csv") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "worker",
        "epoch",
        "amount",
        "canonical_payload_hash",
        "signature_scheme",
        "verification_result",
        "timestamp",
        "network",
        "tx_hash",
    ]
    with open(path, "w", encoding="utf-8", newline="") as ledger_file:
        writer = csv.DictWriter(ledger_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "worker": row["payload"].get("worker") or row["payload"].get("destination"),
                    "epoch": row["payload"].get("id"),
                    "amount": row["payload"].get("amount"),
                    "canonical_payload_hash": row.get("hash"),
                    "signature_scheme": row.get("scheme"),
                    "verification_result": row.get("verification_result"),
                    "timestamp": row["payload"].get("timestamp", ""),
                    "network": row.get("network"),
                    "tx_hash": row.get("tx_hash"),
                }
            )


async def _main() -> None:
    workers = build_demo_workers()
    manager = SwarmManager(workers)
    results = await manager.run()
    write_ledger(results)
    print(f"[X402-NATIVE] workers={len(workers)} receipts={len(results)}")


if __name__ == "__main__":
    asyncio.run(_main())
