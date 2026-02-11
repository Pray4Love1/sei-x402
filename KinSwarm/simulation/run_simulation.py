"""Direct-run local x402 simulation entrypoint with protocol-conformance mapping."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ledger import Ledger
from network_adapter import build_simulation_adapters
from offchain_worker import OffchainWorker
from worker_profile import WorkerProfile

from KinSwarm.config import DEFAULT_NETWORKS, OPERATOR_KEY_PATH
from KinSwarm.offline.x402_reader import (
    encode_x_payment_response,
    map_internal_settlement_to_payment_response,
    map_payment_payload_to_internal_settlement,
)
from offline.signer import OfflineSigner
from soul_sync.agent_credential import AgentCredential
from soul_sync.agent_verifier import AgentVerifier


def ensure_local_signer_key(path: str) -> None:
    key_path = Path(path)
    if not key_path.exists():
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_text("bootstrap-local-signer-key\n", encoding="utf-8")



def generate_wallet_id(worker_name: str) -> str:
    return f"x402w_{hashlib.sha256(worker_name.encode('utf-8')).hexdigest()[:16]}"



def build_x_payment_header(amount: int, network: str = "base-sepolia") -> str:
    payload = {
        "x402Version": 1,
        "scheme": "exact",
        "network": network,
        "payload": {"amount": str(amount), "asset": "USDC", "resource": "/x402/payroll"},
    }
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.b64encode(canonical).decode("utf-8")


async def build_signed_records(
    workers: list[WorkerProfile],
    epoch_id: int,
    signer: OfflineSigner,
    credential: AgentCredential,
) -> list[dict]:
    timestamp = datetime.now(timezone.utc).isoformat()
    records = []

    for worker in workers:
        worker.apply_pto(random.uniform(0, 2))
        amount = worker.calculate_pay()
        wallet_id = generate_wallet_id(worker.name)

        payment_header = build_x_payment_header(amount)
        settlement = map_payment_payload_to_internal_settlement(
            payment_header,
            intent="x402.payroll.settle",
            epoch=str(epoch_id),
            worker=worker.name,
        )

        signed_payload = await credential.sign_payload(
            {
                "id": str(epoch_id),
                "destination": wallet_id,
                "amount": settlement.amount,
                "network": "x402:universal",
                "hours_worked": worker.hours_worked,
                "pto_used": round(worker.pto_used, 2),
                "pto_remaining": worker.pto_remaining,
            }
        )
        verification_result = AgentVerifier.verify(
            signed_payload,
            fallback_key=credential.verification_key,
        )

        response_payload = map_internal_settlement_to_payment_response(
            settlement,
            tx_hash=signer.build_signed_tx({"tx": signed_payload["hash"]})["hash"],
            verification_result=verification_result,
        )
        x_payment_response = encode_x_payment_response(response_payload)

        records.append(
            {
                "worker": worker,
                "wallet_id": wallet_id,
                "epoch": epoch_id,
                "amount": settlement.amount,
                "canonical_payload_hash": signed_payload["hash"],
                "signature_scheme": signed_payload["scheme"],
                "verification_result": verification_result,
                "timestamp": timestamp,
                "x_payment": payment_header,
                "x_payment_response": x_payment_response,
                "signed_payload": signed_payload,
            }
        )

    return records


async def main() -> None:
    workers = [
        WorkerProfile(
            name=f"worker_{i}",
            wage_per_hour=25 + i % 10,
            hours_worked=35 + i % 5,
            pto_allocated=80,
        )
        for i in range(100)
    ]

    ensure_local_signer_key(OPERATOR_KEY_PATH)
    signer = OfflineSigner(OPERATOR_KEY_PATH)
    credential = AgentCredential(OPERATOR_KEY_PATH)
    records = await build_signed_records(workers, epoch_id=0, signer=signer, credential=credential)

    ledger = Ledger()
    adapters = build_simulation_adapters(DEFAULT_NETWORKS)
    worker = OffchainWorker(workers, adapters, ledger)

    print("Running x402 epoch settlement for 100 workers...\n")
    await worker.settle_epoch(records, epoch_id=0)
    expected_networks = {f"x402:{name.lower()}" for name in DEFAULT_NETWORKS}
    ledger.assert_invariants(expected_networks=expected_networks)

    print("\nLedger report (first 10 records):")
    ledger.report(limit=10)


if __name__ == "__main__":
    asyncio.run(main())
