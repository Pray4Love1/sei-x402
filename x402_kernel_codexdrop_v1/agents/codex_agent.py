"""Codex agent for relay signing."""

from __future__ import annotations

from dataclasses import dataclass

from lib.sovereign_signer import SovereignSigner


@dataclass
class CodexAgent:
    signer: SovereignSigner

    def sign_payload(self, payload: dict, index: int) -> str:
        signature = self.signer.sign(payload, index)
        return signature.hex()
