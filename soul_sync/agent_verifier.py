"""Verification helpers for agent-backed signed settlements."""

from __future__ import annotations

from offline.verify import verify_tx


class AgentVerifier:
    """Validates signature integrity plus required agent entropy fields."""

    @staticmethod
    def verify(signed_payload: dict, fallback_key: str | None = None) -> bool:
        payload = signed_payload.get("payload", {})
        has_entropy_fields = bool(payload.get("entropy")) and bool(payload.get("agent_entropy"))
        return has_entropy_fields and verify_tx(signed_payload, fallback_key=fallback_key)
