"""Ephemeral credential signer combining agent seed + Entropy 3.12 commitments."""

from __future__ import annotations

from offline.entropy import entropy_for_header
from offline.signer import OfflineSigner
from soul_sync.agent_entropy_provider import AgentEntropyProvider


class AgentCredential:
    def __init__(self, operator_key_path: str):
        self._signer = OfflineSigner(operator_key_path)
        self._entropy_provider = AgentEntropyProvider()

    @property
    def verification_key(self) -> str:
        """Local-only verification key for strict fallback verification."""
        return self._signer.private_key

    async def sign_payload(self, payload: dict) -> dict:
        tx_payload = dict(payload)
        header_id = str(tx_payload.get("id", "unknown"))
        agent_entropy = await self._entropy_provider.generate_ephemeral_seed()
        commitment = entropy_for_header(header_id, session_noise=agent_entropy.encode("utf-8"))

        tx_payload["agent_entropy"] = agent_entropy
        tx_payload["entropy"] = commitment.hex()
        return self._signer.build_signed_tx(tx_payload)
