"""Kin agent for signing and submitting payments."""

from __future__ import annotations

from dataclasses import dataclass

from lib.sovereign_signer import SovereignSigner


@dataclass
class KinAgent:
    signer: SovereignSigner

    def sign_payload(self, payload: dict, index: int) -> str:
        signature = self.signer.sign(payload, index)
        return signature.hex()
