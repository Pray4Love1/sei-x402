"""Worker agent primitives including wage/PTO-aware settlement payloads."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from soul_sync.agent_credential import AgentCredential
from soul_sync.agent_verifier import AgentVerifier


@dataclass
class WorkerProfile:
    worker_id: str
    wage_per_hour: int
    hours_worked: int = 0
    pto_allocated: int = 0
    pto_used: int = 0

    def calculate_net_amount(self) -> int:
        pto_hours_paid = min(self.pto_used, self.pto_allocated)
        return (self.hours_worked + pto_hours_paid) * self.wage_per_hour

    def remaining_pto(self) -> int:
        return max(self.pto_allocated - self.pto_used, 0)


class WorkerAgent:
    def __init__(self, profile: WorkerProfile, agent_credential: AgentCredential):
        self.profile = profile
        self.credential = agent_credential
        self.ledger: list[dict] = []

    async def settle(self, epoch_id: str) -> dict:
        payload = {
            "id": epoch_id,
            "destination": self.profile.worker_id,
            "amount": self.profile.calculate_net_amount(),
            "hours_worked": self.profile.hours_worked,
            "pto_used": self.profile.pto_used,
            "pto_remaining": self.profile.remaining_pto(),
            "profile": asdict(self.profile),
        }
        signed_tx = await self.credential.sign_payload(payload)
        self.ledger.append(signed_tx)
        return signed_tx

    def validate_settlement(self, signed_tx: dict) -> bool:
        return AgentVerifier.verify(signed_tx, fallback_key=self.credential.verification_key)
