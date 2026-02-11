"""In-memory ledger for local x402 simulation runs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LedgerRecord:
    worker_name: str
    wallet_id: str
    epoch: int
    amount: int
    canonical_payload_hash: str
    signature_scheme: str
    verification_result: bool
    timestamp: str
    network: str
    tx_hash: str


class Ledger:
    def __init__(self) -> None:
        self.records: list[LedgerRecord] = []

    def record(self, record: LedgerRecord) -> None:
        self.records.append(record)

    def assert_invariants(self, expected_networks: set[str] | None = None) -> None:
        assert self.records, "ledger must not be empty"
        assert all(row.verification_result for row in self.records), "verification failures detected"

        if expected_networks is not None:
            actual_networks = {row.network for row in self.records}
            assert actual_networks == expected_networks, (
                f"network mismatch: expected={sorted(expected_networks)} actual={sorted(actual_networks)}"
            )

    def report(self, limit: int = 10) -> None:
        for row in self.records[:limit]:
            print(
                f"Worker {row.worker_name} | Wallet {row.wallet_id} | Epoch {row.epoch} | Paid {row.amount} | "
                f"hash={row.canonical_payload_hash[:16]}... | scheme={row.signature_scheme} | "
                f"verified={row.verification_result} | ts={row.timestamp} | {row.network} tx={row.tx_hash[:16]}..."
            )
